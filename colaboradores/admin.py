from django.contrib import admin
from .models import Colaborador

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'cpf', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'matricula', 'cpf')
