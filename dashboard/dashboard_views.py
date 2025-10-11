
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.apps import apps
@login_required

def dashboard_view(request):
    """Dashboard simples com métricas do dia e pendências.
    Evita NameError usando apps.get_model em vez de acessar settings diretamente.
    """
    pendencias = 0
    emprestimos_hoje = 0
    try:
        Emprestimo = apps.get_model('epi', 'Emprestimo')
        EmprestimoItem = apps.get_model('epi', 'EmprestimoItem')
        hoje_inicio = timezone.localdate()
        emprestimos_hoje = Emprestimo.objects.filter(criado_em__date=hoje_inicio).count()
        PENDENTES = ['EMPRESTADO', 'EM_USO']
        pendencias = EmprestimoItem.objects.filter(devolvido_em__isnull=True, status__in=PENDENTES).count()
    except Exception:
        pass

    return render(request, "dashboard/dashboard.html", {
        "emprestimos_hoje": emprestimos_hoje,
        "pendencias": pendencias,
    })
