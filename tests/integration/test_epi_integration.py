import pytest
from django.urls import reverse
from epi.models import Epi

@pytest.mark.django_db
def test_listagem_status_200(client):
    """Testa se a página de listagem de EPIs retorna status 200"""
    resp = client.get(reverse("epi:list"))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_criacao_ok(client):
    """Testa se um novo EPI é criado corretamente"""
    data = {"codigo": "LUV-123", "nome": "Luva", "tamanho": "M", "estoque": 5, "ativo": True}
    resp = client.post(reverse("epi:create"), data, follow=True)
    assert resp.status_code == 200
    assert Epi.objects.filter(codigo="LUV-123").exists()


@pytest.mark.django_db
def test_atualizacao_ok(client):
    """Testa se a atualização de um EPI funciona corretamente"""
    e = Epi.objects.create(codigo="LUV-001", nome="Luva", tamanho="P", estoque=2, ativo=True)
    data = {"codigo": "LUV-001", "nome": "Luva Nitrílica", "tamanho": "M", "estoque": 3, "ativo": True}
    resp = client.post(reverse("epi:update", args=[e.id]), data, follow=True)
    assert resp.status_code == 200
    e.refresh_from_db()
    assert e.nome == "Luva Nitrílica"


@pytest.mark.django_db
def test_exclusao_ok(client):
    """Testa se a exclusão de um EPI funciona corretamente"""
    e = Epi.objects.create(codigo="CAP-001", nome="Capacete", tamanho="", estoque=1, ativo=True)
    resp = client.post(reverse("epi:delete", args=[e.id]), follow=True)
    assert resp.status_code == 200
    assert not Epi.objects.filter(id=e.id).exists()


@pytest.mark.django_db
def test_pesquisa_parametro_q(client):
    """Testa se a busca por nome (query param ?q=) retorna corretamente"""
    Epi.objects.create(codigo="OCU-9", nome="Óculos", tamanho="", estoque=10, ativo=True)
    resp = client.get(reverse("epi:list") + "?q=Ócu")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_download_csv(client):
    """Testa se o endpoint de exportação CSV de EPIs funciona corretamente"""
    Epi.objects.create(codigo="LUV-777", nome="Luva", tamanho="M", estoque=7, ativo=True)
    resp = client.get(reverse("epi:epis_csv"))
    assert resp.status_code == 200
    assert "text/csv" in resp["Content-Type"]
    assert "colaboradores.csv" not in resp["Content-Disposition"]  
