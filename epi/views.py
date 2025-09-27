from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, Case, When, Value, BooleanField
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv

from .models import Epi, Emprestimo, EmprestimoItem
from .forms import EpiForm, EmprestimoForm, EmprestimoItemFormSet, EmprestimoItemForm


# ======================= EPIs =======================
def epi_list(request):
    q = request.GET.get("q", "")
    only_ca = request.GET.get("ca_vencido")
    qs = Epi.objects.all()
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(codigo__icontains=q) | Q(ca_numero__icontains=q))

    hoje = timezone.localdate()
    if only_ca in ("1", "true", "on", "True"):
        qs = qs.filter(ca_validade__isnull=False, ca_validade__lt=hoje)

    # Cards-resumo
    ca_vencidos = Epi.objects.filter(ca_validade__isnull=False, ca_validade__lt=hoje).count()
    total_epis = Epi.objects.count()
    ativos = Epi.objects.filter(ativo=True).count()
    estoque_zerado = Epi.objects.filter(estoque__lte=0).count()

    paginator = Paginator(qs.order_by("nome"), 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "epi/epi_list.html", {
        "epis": page_obj, "q": q, "ca_vencidos": ca_vencidos,
        "resumo": {"total_epis": total_epis, "ativos": ativos, "ca_vencidos": ca_vencidos, "estoque_zerado": estoque_zerado},
        "page_obj": page_obj,
    })


def epi_create(request):
    if request.method == "POST":
        form = EpiForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "EPI cadastrado com sucesso.")
            return redirect("epi:create")
        else:
            messages.error(request, "Falha ao cadastrar EPI. Verifique os campos.")
    else:
        form = EpiForm()
    return render(request, "epi/epi_form.html", {"form": form, "is_create": True})


def epi_update(request, pk: int):
    obj = get_object_or_404(Epi, pk=pk)
    if request.method == "POST":
        form = EpiForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "EPI atualizado com sucesso.")
            return redirect("epi:update", pk=obj.pk)
        else:
            messages.error(request, "Falha ao atualizar EPI. Verifique os campos.")
    else:
        form = EpiForm(instance=obj)
    return render(request, "epi/epi_form.html", {"form": form, "is_create": False, "obj": obj})


def epi_delete(request, pk: int):
    obj = get_object_or_404(Epi, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "EPI excluído com sucesso.")
    else:
        messages.warning(request, "Operação inválida. Use POST para excluir.")
    return redirect("epi:epi_list") if False else redirect("epi:epi_list".replace("epi_list", "list"))  # compat c/ urls name 'list'


def epis_csv(request):
    q = request.GET.get("q", "")
    only_ca = request.GET.get("ca_vencido")
    qs = Epi.objects.all()
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(codigo__icontains=q) | Q(ca_numero__icontains=q))
    if only_ca in ("1", "true", "on", "True"):
        hoje = timezone.localdate()
        qs = qs.filter(ca_validade__isnull=False, ca_validade__lt=hoje)

    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="epis.csv"'
    w = csv.writer(resp)
    w.writerow(["codigo", "nome", "tamanho", "ca_numero", "ca_validade", "estoque", "ativo"])
    for e in qs.order_by("nome"):
        w.writerow([e.codigo, e.nome, e.tamanho or "", e.ca_numero or "", e.ca_validade or "", e.estoque, "sim" if e.ativo else "nao"])
    return resp


# ===================== Empréstimos =====================
def emprestimo_list(request):
    from datetime import timedelta
    q = request.GET.get("q", "")
    only_late = request.GET.get("atrasados")
    only_soon = request.GET.get("vence_breve")
    only_pend = request.GET.get("pendentes")

    pend_status = ["EMPRESTADO", "EM_USO"]
    now = timezone.now()
    soon_end = now + timedelta(hours=48)

    base = (
        Emprestimo.objects.select_related("colaborador")
        .annotate(
            pendentes=Count("itens", filter=Q(itens__devolvido_em__isnull=True, itens__status__in=pend_status))
        )
        .annotate(
            atrasado=Case(When(previsao_devolucao__lt=now, pendentes__gt=0, then=Value(True)), default=Value(False), output_field=BooleanField()),
            vence_breve=Case(When(previsao_devolucao__gte=now, previsao_devolucao__lte=soon_end, pendentes__gt=0, then=Value(True)), default=Value(False), output_field=BooleanField()),
        )
        .order_by("-id")
    )
    if q:
        base = base.filter(Q(colaborador__nome__icontains=q))
    if only_late in ("1", "true", "on", "True"):
        base = base.filter(atrasado=True)
    if only_soon in ("1", "true", "on", "True"):
        base = base.filter(vence_breve=True)
    if only_pend in ("1", "true", "on", "True"):
        base = base.filter(pendentes__gt=0)

    resumo = {
        "pendentes": base.filter(pendentes__gt=0).count(),
        "atrasados": base.filter(atrasado=True).count(),
        "vence_breve": base.filter(vence_breve=True).count(),
    }

    paginator = Paginator(base, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "epi/emprestimo_list.html", {"emprestimos": page_obj, "q": q, "atrasados": only_late in ("1","true","on","True"), "resumo": resumo, "page_obj": page_obj})


def emprestimo_create(request):
    if request.method == "POST":
        form = EmprestimoForm(request.POST)
        formset = EmprestimoItemFormSet(request.POST, prefix="itens", instance=Emprestimo(), form_kwargs={"creating": True})
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                emp = form.save()
                formset.instance = emp
                formset.save()
            messages.success(request, "Empréstimo registrado com sucesso.")
            return redirect("epi:emprestimo_create")
        else:
            messages.error(request, "Falha ao registrar empréstimo. Verifique os campos.")
    else:
        form = EmprestimoForm()
        formset = EmprestimoItemFormSet(prefix="itens", instance=Emprestimo(), form_kwargs={"creating": True})
    return render(request, "epi/emprestimo_form.html", {"form": form, "formset": formset, "is_create": True})


def emprestimo_edit(request, pk: int):
    emp = get_object_or_404(Emprestimo, pk=pk)
    if request.method == "POST":
        form = EmprestimoForm(request.POST, instance=emp)
        formset = EmprestimoItemFormSet(request.POST, prefix="itens", instance=emp)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Empréstimo atualizado com sucesso.")
            return redirect("epi:emprestimo_edit", pk=emp.pk)
        else:
            messages.error(request, "Falha ao atualizar empréstimo. Verifique os campos.")
    else:
        form = EmprestimoForm(instance=emp)
        formset = EmprestimoItemFormSet(prefix="itens", instance=emp)
    return render(request, "epi/emprestimo_form.html", {"form": form, "formset": formset, "is_create": False, "obj": emp})


def emprestimos_csv(request):
    from datetime import timedelta
    q = request.GET.get("q","")
    only_late = request.GET.get("atrasados")
    only_soon = request.GET.get("vence_breve")
    only_pend = request.GET.get("pendentes")
    now = timezone.now()
    soon_end = now + timedelta(hours=48)
    pend_status = ["EMPRESTADO", "EM_USO"]

    qs = (Emprestimo.objects.select_related("colaborador")
        .annotate(pendentes=Count("itens", filter=Q(itens__devolvido_em__isnull=True, itens__status__in=pend_status)))
        .annotate(
            atrasado=Case(When(previsao_devolucao__lt=now, pendentes__gt=0, then=Value(True)), default=Value(False), output_field=BooleanField()),
            vence_breve=Case(When(previsao_devolucao__gte=now, previsao_devolucao__lte=soon_end, pendentes__gt=0, then=Value(True)), default=Value(False), output_field=BooleanField()),
        )
        .order_by("-id")
    )
    if q:
        qs = qs.filter(Q(colaborador__nome__icontains=q))
    if only_late in ("1","true","on","True"):
        qs = qs.filter(atrasado=True)
    if only_soon in ("1","true","on","True"):
        qs = qs.filter(vence_breve=True)
    if only_pend in ("1","true","on","True"):
        qs = qs.filter(pendentes__gt=0)

    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="emprestimos.csv"'
    w = csv.writer(resp)
    w.writerow(["id","colaborador","previsao_devolucao","pendentes","status","atrasado","vence_breve"])
    for e in qs:
        w.writerow([e.id, e.colaborador.nome, e.previsao_devolucao, e.pendentes, getattr(e, "status", ""), "sim" if e.atrasado else "nao", "sim" if e.vence_breve else "nao"])
    return resp


# ===================== Relatórios =====================
def relatorio_colaborador(request):
    nome = request.GET.get("nome", "")
    itens = EmprestimoItem.objects.select_related("emprestimo", "epi", "emprestimo__colaborador")
    if nome:
        itens = itens.filter(emprestimo__colaborador__nome__icontains=nome)
    itens = itens.order_by("-emprestimo__criado_em")
    return render(request, "epi/relatorio_colaborador.html", {"itens": itens, "nome": nome})


def relatorio_colaborador_csv(request):
    nome = request.GET.get("nome", "")
    itens = EmprestimoItem.objects.select_related("emprestimo", "epi", "emprestimo__colaborador")
    if nome:
        itens = itens.filter(emprestimo__colaborador__nome__icontains=nome)
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="relatorio_colaborador.csv"'
    w = csv.writer(resp)
    w.writerow(["colaborador","epi","quantidade","data_emprestimo","prev_devolucao","status","devolvido_em"])
    for i in itens:
        w.writerow([i.emprestimo.colaborador.nome, i.epi.nome, i.quantidade, i.emprestimo.criado_em, i.emprestimo.previsao_devolucao, i.get_status_display(), i.devolvido_em or ""])
    return resp

from django import forms


def relatorios(request):
    nome = request.GET.get("nome", "").strip()
    epi_nome = request.GET.get("epi", "").strip()
    status = request.GET.get("status", "").strip()

    itens = (EmprestimoItem.objects
             .select_related("emprestimo", "epi", "emprestimo__colaborador")
             .order_by("-emprestimo__criado_em"))

    # Filtros AND
    if nome:
        itens = itens.filter(emprestimo__colaborador__nome__icontains=nome)
    if epi_nome:
        itens = itens.filter(epi__nome__icontains=epi_nome)
    if status:
        itens = itens.filter(status=status)

    return render(request, "epi/relatorios.html", {
        "itens": itens,
        "nome": nome,
        "epi": epi_nome,
        "status": status,
        "status_choices": EmprestimoItem._meta.get_field("status").choices,
    })
