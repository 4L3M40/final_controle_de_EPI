# epi/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import Epi, Emprestimo, EmprestimoItem

# Estados conforme o enunciado
PENDENTES = {"EMPRESTADO", "EM_USO", "FORNECIDO"}
RETORNOS = {"DEVOLVIDO", "DANIFICADO", "PERDIDO"}


# -----------------------------------------
# EPI
# -----------------------------------------
class EpiForm(forms.ModelForm):
    class Meta:
        model = Epi
        fields = ["codigo", "nome", "tamanho", "ca_numero", "ca_validade", "estoque", "ativo"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "tamanho": forms.TextInput(attrs={"class": "form-control"}),
            "ca_numero": forms.TextInput(attrs={"class": "form-control"}),
            "ca_validade": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "estoque": forms.NumberInput(attrs={"min": 0, "class": "form-control"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# -----------------------------------------
# Empréstimo (cabeçalho)
# -----------------------------------------
class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ["colaborador", "previsao_devolucao"]
        widgets = {
            "colaborador": forms.Select(attrs={"class": "form-select"}),
            "previsao_devolucao": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # guarda o valor original para permitir manter data passada ao editar
        # Desabilita campos ao editar
        if self.instance and getattr(self.instance, 'pk', None):
            self.fields['colaborador'].disabled = True
            self.fields['previsao_devolucao'].disabled = True

        self._orig_prev = None
        if self.instance and getattr(self.instance, "pk", None):
            self._orig_prev = self.instance.previsao_devolucao

    def _aware(self, dt):
        if not dt:
            return dt
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    def clean_previsao_devolucao(self):
        prev = self.cleaned_data.get("previsao_devolucao")
        if prev is None:
            return prev

        prev = self._aware(prev)
        now = timezone.now()

        # Se está editando e a data não mudou (mesmo que seja passada), permite.
        if self.instance and self.instance.pk and self._orig_prev:
            orig = self._aware(self._orig_prev)
            if prev == orig:
                return prev

        # Para novos valores (ou criação), exige futuro.
        if prev <= now:
            raise forms.ValidationError("A data prevista de devolução deve ser posterior à data/hora atual.")
        return prev


# -----------------------------------------
# Itens do Empréstimo (linhas)
# -----------------------------------------
class EmprestimoItemForm(forms.ModelForm):
    """
    Quando 'creating=True':
      - Esconde 'devolvido_em' e 'observacao_devolucao';
      - Restringe os choices de 'status' a {EMPRESTADO, EM_USO, FORNECIDO}.
    Em edição, todos os status são exibidos.
    """
    class Meta:
        model = EmprestimoItem
        fields = ["epi", "quantidade", "status", "devolvido_em", "observacao_devolucao"]
        widgets = {
            "epi": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={"min": 1, "class": "form-control form-control-sm"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "devolvido_em": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "observacao_devolucao": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.creating = kwargs.pop("creating", False)
        super().__init__(*args, **kwargs)

        if self.creating:
            # Oculta campos só usados em retorno
            self.fields["devolvido_em"].widget = forms.HiddenInput()
            self.fields["observacao_devolucao"].widget = forms.HiddenInput()

            # Limita status na criação
            permitidos = PENDENTES
            self.fields["status"].choices = [
                (value, label) for (value, label) in self.fields["status"].choices if value in permitidos
            ]
            # Status inicial sugerido
            if not self.initial.get("status"):
                self.initial["status"] = "EMPRESTADO"

    def clean(self):
        cleaned = super().clean()
        epi = cleaned.get("epi")
        qtd = cleaned.get("quantidade") or 0
        status = cleaned.get("status")
        devolvido_em = cleaned.get("devolvido_em")
        obs = cleaned.get("observacao_devolucao")

        # Converte devolvido_em para timezone-aware, se vier do input local
        if devolvido_em and timezone.is_naive(devolvido_em):
            cleaned["devolvido_em"] = timezone.make_aware(devolvido_em, timezone.get_current_timezone())

        # Regras quando é status de retorno
        if status in RETORNOS:
            if cleaned.get("devolvido_em") is None:
                self.add_error("devolvido_em", "Informe a data/hora da devolução para este status.")
            if status in {"DANIFICADO", "PERDIDO"} and not obs:
                self.add_error("observacao_devolucao", "Descreva a observação na devolução.")
        else:
            # Em circulação: quantidade > 0 e estoque suficiente
            if qtd <= 0:
                self.add_error("quantidade", "Quantidade deve ser maior que zero.")
            if epi:
                disponivel = epi.estoque
                # Se estiver editando, devolve a quantidade original ao disponível
                if self.instance and self.instance.pk:
                    orig_pendente = (self.instance.devolvido_em is None and self.instance.status in PENDENTES)
                    if orig_pendente:
                        disponivel += (self.instance.quantidade or 0)
                if qtd > disponivel:
                    self.add_error("quantidade", f"Estoque insuficiente para {epi.nome}. Disponível: {disponivel}.")

        return cleaned


# Formset (passar creating=True na view de criação)
EmprestimoItemFormSet = inlineformset_factory(
    Emprestimo,
    EmprestimoItem,
    form=EmprestimoItemForm,
    extra=1,
    can_delete=True,
)
