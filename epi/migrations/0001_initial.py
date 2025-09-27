
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('colaboradores', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Epi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=30, unique=True)),
                ('nome', models.CharField(max_length=200)),
                ('tamanho', models.CharField(blank=True, max_length=30)),
                ('ca_numero', models.CharField(blank=True, max_length=30, verbose_name='Nº CA')),
                ('ca_validade', models.DateField(blank=True, null=True, verbose_name='Validade do CA')),
                ('estoque', models.PositiveIntegerField(default=0)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['nome'], 'verbose_name': 'EPI', 'verbose_name_plural': 'EPIs'},
        ),
        migrations.CreateModel(
            name='Emprestimo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('previsao_devolucao', models.DateTimeField()),
                ('colaborador', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='emprestimos', to='colaboradores.colaborador')),
            ],
            options={'ordering': ['-criado_em']},
        ),
        migrations.CreateModel(
            name='EmprestimoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField()),
                ('entregue_em', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('EMPRESTADO', 'Emprestado'), ('EM_USO', 'Em Uso'), ('FORNECIDO', 'Fornecido'), ('DEVOLVIDO', 'Devolvido'), ('DANIFICADO', 'Danificado'), ('PERDIDO', 'Perdido')], default='EMPRESTADO', max_length=20)),
                ('devolvido_em', models.DateTimeField(blank=True, null=True)),
                ('observacao_devolucao', models.TextField(blank=True)),
                ('emprestimo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='epi.emprestimo')),
                ('epi', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='itens', to='epi.epi')),
            ],
            options={'verbose_name': 'Item do Empréstimo', 'verbose_name_plural': 'Itens do Empréstimo'},
        ),
    ]
