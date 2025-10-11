
import pytest
from django.core.exceptions import ValidationError
from colaboradores.models import Colaborador

@pytest.mark.django_db
def test_criacao_colaborador_str():
    c = Colaborador.objects.create(nome="Ana Silva", cpf="12345678901", matricula="MAT001")
    assert str(c) == "Ana Silva (MAT001)"

@pytest.mark.django_db
def test_cpf_deve_ter_11_digitos():
    c = Colaborador(nome="Joao", cpf="123", matricula="MAT002")
    with pytest.raises(ValidationError):
        c.full_clean()

@pytest.mark.django_db
def test_cpf_unico():
    Colaborador.objects.create(nome="A", cpf="11111111111", matricula="MAT010")
    c2 = Colaborador(nome="B", cpf="11111111111", matricula="MAT011")
    with pytest.raises(ValidationError):
        c2.full_clean()
