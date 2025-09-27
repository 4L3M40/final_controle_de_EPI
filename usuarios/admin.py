from django.contrib import admin
from .models import Colaborador

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome", "matricula", "perfil", "ativo", "usuario")
    list_filter = ("perfil", "ativo")
    search_fields = ("nome", "matricula", "cpf")

    def has_add_permission(self, request):
        return request.user.is_superuser or getattr(request.user, "perfil", "") == "ADMIN"

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or getattr(request.user, "perfil", "") == "ADMIN"

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or getattr(request.user, "perfil", "") == "ADMIN"

    def get_readonly_fields(self, request, obj=None):
        if not (request.user.is_superuser or getattr(request.user, "perfil", "") == "ADMIN"):
            return ("nome", "matricula", "cpf", "perfil", "ativo", "usuario")
        return ()
