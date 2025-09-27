
# colaboradores/forms.py
from django import forms
from .models import Colaborador
import re

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["matricula", "nome", "cpf", "ativo"]
        widgets = {
            "matricula": forms.TextInput(attrs={"class":"form-control"}),
            "nome": forms.TextInput(attrs={"class":"form-control"}),
            "cpf": forms.TextInput(attrs={"class":"form-control"}),
            "ativo": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf", "")
        cpf_digits = re.sub(r"\D+", "", cpf)
        if len(cpf_digits) != 11:
            raise forms.ValidationError("CPF deve ter 11 dígitos (somente números)." )
        return cpf_digits

    def clean_matricula(self):
        m = (self.cleaned_data.get("matricula") or "").strip()
        if not m:
            raise forms.ValidationError("Matrícula é obrigatória.")
        return m
