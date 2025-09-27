from django import forms
from django.contrib.auth.models import User
from .models import Colaborador

class ColaboradorForm(forms.ModelForm):
    username = forms.CharField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Colaborador
        fields = ['nome', 'cpf', 'matricula', 'perfil', 'ativo']

    def save(self, commit=True):
        colaborador = super().save(commit=False)
        perfil = self.cleaned_data['perfil']

        # Criar usuário apenas se for técnico ou almoxarife
        if perfil in ['TECNICO_SST', 'ALMOXARIFE']:
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            if username and password:
                user = User.objects.create_user(username=username, password=password)
                colaborador.usuario = user

        if commit:
            colaborador.save()
        return colaborador
