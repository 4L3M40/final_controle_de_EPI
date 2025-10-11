
import pytest
from django.urls import reverse

def test_rota_dashboard_home_reverse():
    assert reverse("dashboard_home") == "/"

def test_rota_dashboard_reverse():
    assert reverse("dashboard") == "/dashboard/"

def test_rotas_colaboradores_reverse():
    assert reverse("colaboradores:list") == "/colaboradores/"
    assert reverse("colaboradores:create") == "/colaboradores/novo/"

def test_rotas_epi_reverse():
    assert reverse("epi:list") == "/epis/"
    assert reverse("epi:create") == "/epis/novo/"

@pytest.mark.django_db
def test_dashboard_status_302_quando_deslogado(client):
    resp = client.get(reverse("dashboard"))
    assert resp.status_code == 302
    assert "/usuarios/login/" in resp.url

@pytest.mark.django_db
def test_dashboard_status_200_quando_logado(client, django_user_model):
    django_user_model.objects.create_user(username="admin", password="admin")
    client.login(username="admin", password="admin")
    resp = client.get(reverse("dashboard"))
    assert resp.status_code == 200

@pytest.mark.django_db
def test_lista_colaboradores_status_200(client):
    resp = client.get(reverse("colaboradores:list"))
    assert resp.status_code == 200

@pytest.mark.django_db
def test_lista_epis_status_200(client):
    resp = client.get(reverse("epi:list"))
    assert resp.status_code == 200

@pytest.mark.django_db
def test_criar_colaborador_via_post(client):
    data = {"nome":"Ana","cpf":"12345678901","matricula":"M001","ativo":True}
    resp = client.post(reverse("colaboradores:create"), data, follow=True)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_criar_epi_via_post(client):
    data = {"codigo":"LUV-123","nome":"Luva","tamanho":"M","estoque":5,"ativo":True}
    resp = client.post(reverse("epi:create"), data, follow=True)
    assert resp.status_code == 200
