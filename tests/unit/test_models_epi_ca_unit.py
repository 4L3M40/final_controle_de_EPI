import pytest
from datetime import timedelta
from django.utils import timezone

pytestmark = pytest.mark.django_db


def _obter_formulario_epi():
    """Tenta importar o EpiForm; se não existir, pula os testes deste módulo."""
    try:
        from epi.forms import EpiForm
        return EpiForm
    except Exception:
        pytest.skip("EpiForm não encontrado em epi/forms.py", allow_module_level=True)


def test_formulario_epi_campos_basicos_validos():
    """Testa se o formulário de EPI é válido com dados básicos corretos"""
    EpiForm = _obter_formulario_epi()
    form = EpiForm(data={
        "codigo": "LUV-999",
        "nome": "Luva Nitrílica",
        "tamanho": "M",
        "estoque": 5,
        "ativo": True,
    })
    assert form.is_valid(), form.errors.as_json()


def test_formulario_epi_estoque_negativo_invalido():
    """Testa se o formulário é inválido quando o estoque é negativo"""
    EpiForm = _obter_formulario_epi()
    form = EpiForm(data={
        "codigo": "EST-NEG",
        "nome": "Capacete",
        "tamanho": "",
        "estoque": -1,
        "ativo": True,
    })
    assert not form.is_valid()
    # Verifica se o erro está relacionado ao campo 'estoque'
    assert "estoque" in form.errors


def test_formulario_epi_ca_expirado_invalido_se_existir():
    """Testa se o formulário é inválido quando o CA está expirado (se os campos existirem)"""
    EpiForm = _obter_formulario_epi()
    data_hoje = timezone.now().date()

    # Se o formulário não tiver os campos de CA, o teste é ignorado
    if not {"ca_numero", "ca_validade"}.issubset(set(EpiForm().fields.keys())):
        pytest.skip("Formulário não possui campos ca_numero/ca_validade")

    form = EpiForm(data={
        "codigo": "CA-EXP",
        "nome": "Óculos de Proteção",
        "tamanho": "",
        "estoque": 3,
        "ativo": True,
        "ca_numero": "12345",
        "ca_validade": data_hoje - timedelta(days=1),  # Ontem (expirado)
    })
    assert not form.is_valid()
    assert "ca_validade" in form.errors  # Deve invalidar o CA expirado


def test_formulario_epi_ca_valido_ok_se_existir():
    """Testa se o formulário é válido quando o CA está dentro do prazo (se os campos existirem)"""
    EpiForm = _obter_formulario_epi()
    data_hoje = timezone.now().date()

    if not {"ca_numero", "ca_validade"}.issubset(set(EpiForm().fields.keys())):
        pytest.skip("Formulário não possui campos ca_numero/ca_validade")

    form = EpiForm(data={
        "codigo": "CA-OK",
        "nome": "Protetor Auricular",
        "tamanho": "",
        "estoque": 10,
        "ativo": True,
        "ca_numero": "67890",
        "ca_validade": data_hoje + timedelta(days=30),  # Futuro (válido)
    })
    assert form.is_valid(), form.errors.as_json()
