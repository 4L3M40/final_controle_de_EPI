from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv

from .models import Colaborador
from .forms import ColaboradorForm


def list_colaboradores(request):
    q = request.GET.get("q", "")
    objs = Colaborador.objects.all()
    if q:
        objs = objs.filter(
            Q(nome__icontains=q) | Q(matricula__icontains=q) | Q(cpf__icontains=q)
        ).distinct()
    paginator = Paginator(objs.order_by("nome"), 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "colaboradores/colaborador_list.html",
        {"colaboradores": page_obj, "q": q, "page_obj": page_obj},
    )


def create_colaborador(request):
    if request.method == "POST":
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Colaborador cadastrado com sucesso.")
            # permanecer na tela de cadastro:
            return redirect("colaboradores:create")
        else:
            messages.error(request, "Falha ao cadastrar colaborador. Verifique os campos.")
    else:
        form = ColaboradorForm()
    return render(request, "colaboradores/colaborador_form.html", {"form": form, "is_create": True})


def update_colaborador(request, pk: int):
    obj = get_object_or_404(Colaborador, pk=pk)
    if request.method == "POST":
        form = ColaboradorForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Colaborador atualizado com sucesso.")
            # manter na tela de edição
            return redirect("colaboradores:update", pk=obj.pk)
        else:
            messages.error(request, "Falha ao atualizar colaborador. Verifique os campos.")
    else:
        form = ColaboradorForm(instance=obj)
    return render(request, "colaboradores/colaborador_form.html", {"form": form, "is_create": False, "obj": obj})


def delete_colaborador(request, pk: int):
    obj = get_object_or_404(Colaborador, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Colaborador excluído com sucesso.")
    else:
        messages.warning(request, "Operação inválida. Use POST para excluir.")
    return redirect("colaboradores:list")


def colaboradores_csv(request):
    q = request.GET.get("q", "")
    qs = Colaborador.objects.all()
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) | Q(matricula__icontains=q) | Q(cpf__icontains=q)
        ).distinct()

    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="colaboradores.csv"'
    w = csv.writer(resp)
    w.writerow(["id", "matricula", "nome", "cpf", "ativo"])
    for c in qs.order_by("nome"):
        w.writerow([c.id, c.matricula, c.nome, c.cpf, "sim" if c.ativo else "nao"])
    return resp
