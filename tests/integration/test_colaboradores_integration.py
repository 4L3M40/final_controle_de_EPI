import pytest
from django.urls import reverse
from colaboradores.models import Colaborador

@pytest.mark.django_db
def test_listagem_status_200(client):
    """Testa se a página de listagem retorna status 200"""
    resp = client.get(reverse("colaboradores:list"))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_criacao_ok(client):
    """Testa se um colaborador é criado corretamente"""
    data = {"nome": "Ana", "cpf": "12345678901", "matricula": "M001", "ativo": True}
    resp = client.post(reverse("colaboradores:create"), data, follow=True)
    assert resp.status_code == 200
    assert Colaborador.objects.filter(matricula="M001").exists()


@pytest.mark.django_db
def test_atualizacao_ok(client):
    """Testa se a atualização de um colaborador funciona"""
    c = Colaborador.objects.create(nome="Ana", cpf="12345678901", matricula="M001", ativo=True)
    data = {"nome": "Ana Silva", "cpf": "12345678901", "matricula": "M001", "ativo": True}
    resp = client.post(reverse("colaboradores:update", args=[c.id]), data, follow=True)
    assert resp.status_code == 200
    c.refresh_from_db()
    assert c.nome == "Ana Silva"


@pytest.mark.django_db
def test_exclusao_ok(client):
    """Testa se a exclusão de um colaborador funciona"""
    c = Colaborador.objects.create(nome="Bob", cpf="11111111111", matricula="M002", ativo=True)
    resp = client.post(reverse("colaboradores:delete", args=[c.id]), follow=True)
    assert resp.status_code == 200
    assert not Colaborador.objects.filter(id=c.id).exists()


@pytest.mark.django_db
def test_pesquisa_parametro_q(client):
    """Testa se a pesquisa por nome (query param ?q=) funciona"""
    Colaborador.objects.create(nome="Carlos", cpf="22222222222", matricula="M010", ativo=True)
    resp = client.get(reverse("colaboradores:list") + "?q=Car")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_download_csv(client):
    """Testa se o endpoint de exportação CSV funciona corretamente"""
    Colaborador.objects.create(nome="Eva", cpf="33333333333", matricula="M020", ativo=False)
    resp = client.get(reverse("colaboradores:csv"))
    assert resp.status_code == 200
    assert "text/csv" in resp["Content-Type"]
    assert "colaboradores.csv" in resp["Content-Disposition"]

