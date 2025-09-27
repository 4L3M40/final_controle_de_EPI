from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Epi(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=200)
    tamanho = models.CharField(max_length=30, blank=True)
    ca_numero = models.CharField("Nº CA", max_length=30, blank=True)
    ca_validade = models.DateField("Validade do CA", null=True, blank=True)
    estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "EPI"
        verbose_name_plural = "EPIs"

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    @property
    def is_ca_vencido(self):
        if self.ca_validade:
            return self.ca_validade < timezone.localdate()
        return False


class Emprestimo(models.Model):
    from colaboradores.models import Colaborador

    colaborador = models.ForeignKey(
        Colaborador, on_delete=models.PROTECT, related_name="emprestimos"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    previsao_devolucao = models.DateTimeField()

    class Meta:
        ordering = ["-criado_em"]

    def clean(self):
        if self.previsao_devolucao <= timezone.now():
            raise ValidationError(
                {"previsao_devolucao": "A previsão deve ser posterior à data/hora atual."}
            )

    @property
    def status(self):
        pendentes = self.itens.filter(
            devolvido_em__isnull=True, status__in=["EMPRESTADO", "EM_USO"]
        ).exists()
        return "ABERTO" if pendentes else "FECHADO"

    def __str__(self):
        return f"Empréstimo #{self.pk} - {self.colaborador.nome}"


STATUS_CHOICES = [
    ("EMPRESTADO", "Emprestado"),
    ("EM_USO", "Em Uso"),
    ("FORNECIDO", "Fornecido"),
    ("DEVOLVIDO", "Devolvido"),
    ("DANIFICADO", "Danificado"),
    ("PERDIDO", "Perdido"),
]
PENDENTES = {"EMPRESTADO", "EM_USO", "FORNECIDO"}


class EmprestimoItem(models.Model):
    emprestimo = models.ForeignKey(
        Emprestimo, on_delete=models.CASCADE, related_name="itens"
    )
    epi = models.ForeignKey(Epi, on_delete=models.PROTECT, related_name="itens")
    quantidade = models.PositiveIntegerField()
    entregue_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="EMPRESTADO")
    devolvido_em = models.DateTimeField(null=True, blank=True)
    observacao_devolucao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Item do Empréstimo"
        verbose_name_plural = "Itens do Empréstimo"

    def clean(self):
        if self.quantidade <= 0:
            raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})

        # criação: checa estoque total
        if self.pk is None and self.status in PENDENTES:
            if self.epi.estoque < self.quantidade:
                raise ValidationError({"quantidade": "Estoque insuficiente para o EPI."})

        # edição: se continuar pendente, checa só a diferença
        if self.pk is not None:
            old = EmprestimoItem.objects.get(pk=self.pk)
            if old.status in PENDENTES and self.status in PENDENTES:
                diff = self.quantidade - old.quantidade
                if diff > 0 and self.epi.estoque < diff:
                    raise ValidationError({"quantidade": "Estoque insuficiente para aumentar a quantidade."})

        # status finais exigem devolvido_em
        if self.status in ["DEVOLVIDO", "DANIFICADO", "PERDIDO"] and self.devolvido_em is None:
            self.devolvido_em = timezone.now()

    def save(self, *args, **kwargs):
        from django.db import models as dj_models
        is_new = self.pk is None
        old = EmprestimoItem.objects.get(pk=self.pk) if not is_new else None

        super().save(*args, **kwargs)

        # criação → baixa estoque
        if is_new and self.status in PENDENTES:
            type(self.epi).objects.filter(pk=self.epi_id).update(
                estoque=dj_models.F("estoque") - self.quantidade
            )

        # edição
        if not is_new:
            # ajuste de quantidade enquanto permanece pendente
            if old.status in PENDENTES and self.status in PENDENTES and self.quantidade != old.quantidade:
                diff = self.quantidade - old.quantidade  # + baixa mais; - devolve diferença
                if diff != 0:
                    type(self.epi).objects.filter(pk=self.epi_id).update(
                        estoque=dj_models.F("estoque") - diff
                    )

            # transição para DEVOLVIDO → recompor
            if old.status != "DEVOLVIDO" and self.status == "DEVOLVIDO":
                type(self.epi).objects.filter(pk=self.epi_id).update(
                    estoque=dj_models.F("estoque") + self.quantidade
                )

    def delete(self, *args, **kwargs):
        from django.db import models as dj_models
        # se item ainda está pendente, devolve estoque antes de excluir
        if self.status in PENDENTES and self.devolvido_em is None:
            type(self.epi).objects.filter(pk=self.epi_id).update(
                estoque=dj_models.F("estoque") + self.quantidade
            )
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.epi.nome} x{self.quantidade} ({self.get_status_display()})"
