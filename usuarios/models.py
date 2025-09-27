from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Colaborador(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="colaborador"
    )

    nome = models.CharField(max_length=200)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{11}$', message='CPF deve ter 11 números')]
    )
    PERFIL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('TECNICO_SST', 'Técnico SST'),
        ('ALMOXARIFE', 'Almoxarife'),
        ('COLABORADOR', 'Colaborador'),
    ]
    matricula = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='COLABORADOR')

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.matricula})"
