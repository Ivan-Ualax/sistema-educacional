from django.contrib import admin

from .models import Contrato


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'funcao',
        'secretaria',
        'modalidade',
        'situacao',
        'salario_fixo',
        'criado_em',
    )

    list_filter = (
        'secretaria',
        'modalidade',
        'situacao',
    )

    search_fields = (
        'nome',
        'cpf',
        'rg',
        'funcao',
        'local_trabalho',
        'banco',
    )

    ordering = (
        'nome',
    )

    readonly_fields = (
        'criado_em',
        'atualizado_em',
    )

    fieldsets = (
        (
            'Dados pessoais',
            {
                'fields': (
                    'nome',
                    'cpf',
                    'rg',
                    'data_nascimento',
                )
            },
        ),
        (
            'Contrato',
            {
                'fields': (
                    'funcao',
                    'local_trabalho',
                    'secretaria',
                    'modalidade',
                    'situacao',
                    'salario_fixo',
                )
            },
        ),
        (
            'Dados bancários',
            {
                'fields': (
                    'banco',
                    'agencia',
                    'conta_bancaria',
                )
            },
        ),
        (
            'Controle',
            {
                'fields': (
                    'criado_em',
                    'atualizado_em',
                )
            },
        ),
    )