import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from colaboradores.models import Colaborador
from epi.models import Epi, Emprestimo, EmprestimoItem

# OBS: Se no seu model o campo for "previsao" (e não "previsao_devolucao"),
# troque abaixo "previsao_devolucao" por "previsao".

@pytest.mark.django_db
def test_emprestimo_previsao_deve_ser_futura():
    col = Colaborador.objects.create(nome="Maria Souza", cpf="98765432100", matricula="MAT100")

    # Previsão no passado -> deve falhar
    emp = Emprestimo(colaborador=col, previsao_devolucao=timezone.now() - timedelta(hours=1))
    with pytest.raises(ValidationError):
        emp.full_clean()

    # Previsão no futuro -> deve passar
    emp_ok = Emprestimo(colaborador=col, previsao_devolucao=timezone.now() + timedelta(days=1))
    emp_ok.full_clean()

@pytest.mark.django_db
def test_fluxo_emprestimo_item_reduz_estoque():
    col = Colaborador.objects.create(nome="Maria Souza", cpf="98765432100", matricula="MAT100")
    epi = Epi.objects.create(codigo="LUV-001", nome="Luva Nitrílica", tamanho="M", estoque=10)
    emp = Emprestimo.objects.create(colaborador=col, previsao_devolucao=timezone.now() + timedelta(days=1))

    item = EmprestimoItem(emprestimo=emp, epi=epi, quantidade=3)
    item.full_clean()
    item.save()

    epi.refresh_from_db()
    assert epi.estoque == 7

@pytest.mark.django_db
def test_nao_permite_quantidade_maior_que_estoque():
    col = Colaborador.objects.create(nome="Maria Souza", cpf="98765432100", matricula="MAT100")
    epi = Epi.objects.create(codigo="LUV-001", nome="Luva Nitrílica", tamanho="M", estoque=10)
    emp = Emprestimo.objects.create(colaborador=col, previsao_devolucao=timezone.now() + timedelta(days=1))

    item = EmprestimoItem(emprestimo=emp, epi=epi, quantidade=999)
    with pytest.raises(ValidationError):
        item.full_clean()

@pytest.mark.django_db
def test_devolucao_devolve_estoque_e_define_data():
    col = Colaborador.objects.create(nome="Maria Souza", cpf="98765432100", matricula="MAT100")
    epi = Epi.objects.create(codigo="LUV-001", nome="Luva Nitrílica", tamanho="M", estoque=10)
    emp = Emprestimo.objects.create(colaborador=col, previsao_devolucao=timezone.now() + timedelta(days=1))

    item = EmprestimoItem.objects.create(emprestimo=emp, epi=epi, quantidade=4)
    epi.refresh_from_db()
    assert epi.estoque == 6

    # Ajuste conforme choices do seu model (ex.: "DEVOLVIDO")
    item.status = "DEVOLVIDO"
    item.full_clean()
    item.save()

    epi.refresh_from_db()
    assert epi.estoque == 10
    assert item.devolvido_em is not None

@pytest.mark.django_db
def test_excluir_item_pendente_restaura_estoque():
    col = Colaborador.objects.create(nome="Maria Souza", cpf="98765432100", matricula="MAT100")
    epi = Epi.objects.create(codigo="LUV-001", nome="Luva Nitrílica", tamanho="M", estoque=10)
    emp = Emprestimo.objects.create(colaborador=col, previsao_devolucao=timezone.now() + timedelta(days=1))

    item = EmprestimoItem.objects.create(emprestimo=emp, epi=epi, quantidade=2)
    epi.refresh_from_db()
    assert epi.estoque == 8

    item.delete()
    epi.refresh_from_db()
    assert epi.estoque == 10  # restaurou os 2 ao excluir item pendente
