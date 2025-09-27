
from django.db import models
from django.core.validators import RegexValidator

class Colaborador(models.Model):
    nome = models.CharField(max_length=200)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        help_text="Apenas números",
        validators=[RegexValidator(regex=r'^\d{11}$', message='O CPF deve conter exatamente 11 dígitos numéricos.')]
    )
    matricula = models.CharField(max_length=30, unique=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "colaborador"
        ordering = ["nome"]
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"

    def __str__(self):
        return f"{self.nome} ({self.matricula})"
