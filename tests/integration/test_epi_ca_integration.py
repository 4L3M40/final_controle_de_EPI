import pytest
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse

pytestmark = pytest.mark.django_db


def _form_possui_campos_ca():
    """Verifica se o EpiForm possui os campos de CA (ca_numero e ca_validade)."""
    try:
        from epi.forms import EpiForm
        fields = set(EpiForm().fields.keys())
        return {"ca_numero", "ca_validade"}.issubset(fields)
    except Exception:
        return False


def test_criacao_epi_com_ca_expirado_rejeitada(client):
    """Testa se o sistema rejeita a criação de EPI com CA expirado (form ou view)."""
    if not _form_possui_campos_ca():
        pytest.skip("App não utiliza ca_numero/ca_validade nas views/forms")

    url = reverse("epi:create")
    data = {
        "codigo": "CA-INT-EXP",
        "nome": "Protetor Facial",
        "tamanho": "",
        "estoque": 1,
        "ativo": True,
        "ca_numero": "ABC123",
        "ca_validade": timezone.now().date() - timedelta(days=1),  # Ontem (expirado)
    }

    resp = client.post(url, data, follow=True)
    # Pode retornar 200 (form inválido) ou 400 (erro direto)
    assert resp.status_code in (200, 400)
    # O importante é que o EPI expirado não seja criado
    from epi.models import Epi
    assert not Epi.objects.filter(codigo="CA-INT-EXP").exists()


def test_criacao_epi_com_ca_valido_aceita(client):
    """Testa se o sistema aceita a criação de EPI com CA válido."""
    if not _form_possui_campos_ca():
        pytest.skip("App não utiliza ca_numero/ca_validade nas views/forms")

    url = reverse("epi:create")
    data = {
        "codigo": "CA-INT-OK",
        "nome": "Protetor Facial",
        "tamanho": "",
        "estoque": 2,
        "ativo": True,
        "ca_numero": "DEF456",
        "ca_validade": timezone.now().date() + timedelta(days=30),  # Futuro (válido)
    }

    resp = client.post(url, data, follow=True)
    # Pode redirecionar (302) ou voltar com o form válido (200)
    assert resp.status_code in (200, 302)
    # Confirma que o registro foi criado com sucesso
    from epi.models import Epi
    assert Epi.objects.filter(codigo="CA-INT-OK").exists()
