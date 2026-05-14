from django.db import models


# =========================
# CARGOS
# =========================

class Cargo(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


# =========================
# FUNCIONÁRIOS
# =========================

class Funcionario(models.Model):

    # Tipos de vínculo
    TIPO_VINCULO = (
        ('contratado', 'Contratado'),
        ('concursado', 'Concursado'),
    )

  # Status do funcionário
    STATUS = (
    ('ativo', 'Ativo'),
    ('inativo', 'Inativo'),
    ('demitido', 'Demitido'),
)

    # Dados pessoais
    nome = models.CharField(max_length=150)

    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True
    )

    numero = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    localidade = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    # Dados profissionais
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    carga_horaria = models.IntegerField(
        default=0
    )

    tipo_vinculo = models.CharField(
        max_length=20,
        choices=TIPO_VINCULO,
        default='contratado'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='ativo'
    )

    # Datas
    data_admissao = models.DateField(
        blank=True,
        null=True
    )

    data_demissao = models.DateField(
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nome


# =========================
# HORAS EXTRAS
# =========================

# =========================
# HORAS EXTRAS
# =========================

# =========================
# HORAS EXTRAS
# =========================

# =========================
# HORAS EXTRAS
# =========================

class HoraExtra(models.Model):

    MES_CHOICES = (
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    )

    TIPO_HORA = (
        ('normal', 'Hora Extra Normal'),
        ('f1', 'Hora Extra F1'),
        ('f2', 'Hora Extra F2'),
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_HORA,
        default='normal'
    )

    quantidade_horas = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    mes_referencia = models.IntegerField(
        choices=MES_CHOICES,
        default=1
    )

    ano = models.IntegerField(
        default=2026
    )

    observacao = models.TextField(
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.funcionario.nome} - {self.mes_referencia}/{self.ano}'