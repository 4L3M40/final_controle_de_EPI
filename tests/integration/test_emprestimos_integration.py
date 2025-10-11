
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from colaboradores.models import Colaborador
from epi.models import Epi, Emprestimo, EmprestimoItem

@pytest.mark.django_db
def test_list_status_200(client):
    resp = client.get(reverse("epi:emprestimo_list"))
    assert resp.status_code == 200

@pytest.mark.django_db
def test_list_paginacao_e_filtros_vazios(client):
    resp = client.get(reverse("epi:emprestimo_list") + "?page=1")
    assert resp.status_code == 200

@pytest.mark.django_db
def test_csv_emprestimos(client):
    col = Colaborador.objects.create(nome="Maria", cpf="99999999999", matricula="MAT999", ativo=True)
    epi = Epi.objects.create(codigo="BOT-001", nome="Bota", tamanho="40", estoque=5, ativo=True)
    emp = Emprestimo.objects.create(colaborador=col, previsao_devolucao=timezone.now() + timedelta(days=2))
    EmprestimoItem.objects.create(emprestimo=emp, epi=epi, quantidade=1)
    resp = client.get(reverse("epi:emprestimos_csv"))
    assert resp.status_code == 200
    assert "text/csv" in resp["Content-Type"]

@pytest.mark.django_db
def test_relatorios_status_200(client):
    resp = client.get(reverse("epi:relatorios"))
    assert resp.status_code == 200

@pytest.mark.django_db
def test_relatorio_colaborador_status_200(client):
    col = Colaborador.objects.create(nome="Maria", cpf="99999999999", matricula="MAT999", ativo=True)
    resp = client.get(reverse("epi:relatorio_colaborador") + f"?q={col.cpf}")
    assert resp.status_code == 200
