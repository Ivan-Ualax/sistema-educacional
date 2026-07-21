from django.core.validators import MinValueValidator
from django.db import models


class Contrato(models.Model):
    MODALIDADES = (
        ('credenciamento', 'Credenciamento'),
        ('prestacao', 'Prestação de Serviço'),
    )

    SECRETARIAS = (
        ('administracao', 'Administração e Finanças'),
        ('assistencia', 'Assistência Social'),
        ('agricultura', 'Agricultura'),
        ('educacao', 'Educação'),
        ('infraestrutura', 'Infraestrutura'),
        ('saude', 'Saúde'),
    )

    SITUACOES = (
        ('ativo', 'Ativo'),
        ('demitido', 'Demitido'),
    )

    nome = models.CharField(max_length=150)
    funcao = models.CharField(max_length=150)
    local_trabalho = models.CharField(max_length=150)

    cpf = models.CharField(
        max_length=14,
        unique=True,
        db_index=True,
    )

    rg = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    data_nascimento = models.DateField(
        blank=True,
        null=True,
    )

    banco = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    agencia = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    conta_bancaria = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    salario_fixo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    secretaria = models.CharField(
        max_length=30,
        choices=SECRETARIAS,
        db_index=True,
    )

    modalidade = models.CharField(
        max_length=30,
        choices=MODALIDADES,
        db_index=True,
    )

    situacao = models.CharField(
        max_length=20,
        choices=SITUACOES,
        default='ativo',
        db_index=True,
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        indexes = [
            models.Index(fields=['secretaria', 'modalidade']),
            models.Index(fields=['situacao', 'secretaria']),
        ]

    def __str__(self):
        return f'{self.nome} - {self.get_modalidade_display()}'