from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # HOME
    # =========================

    path(
        '',
        views.home
    ),

    # =========================
    # CADASTRAR FUNCIONÁRIO
    # =========================

    path(
        'funcionarios/cadastrar/',
        views.cadastrar_funcionario
    ),

    # =========================
    # LISTAR FUNCIONÁRIOS
    # =========================

    path(
        'funcionarios/',
        views.funcionarios
    ),

    # =========================
    # ALTERAR STATUS
    # =========================

    path(
        'funcionarios/status/<int:id>/',
        views.alterar_status
    ),

    # =========================
    # EDITAR FUNCIONÁRIO
    # =========================

    path(
        'funcionarios/editar/<int:id>/',
        views.editar_funcionario
    ),

    # =========================
    # EXCLUIR FUNCIONÁRIO
    # =========================

    path(
        'funcionarios/excluir/<int:id>/',
        views.excluir_funcionario
    ),

    path(
    'horas-extras/',
    views.horas_extras
    ),

    path(
    'horas-extras/adicionar/<int:id>/',
    views.adicionar_hora_extra
    ),

    path(
    'relatorio-mensal/',
    views.relatorio_mensal
),
    path(
    'funcionario/<int:id>/horas/',
    views.horas_funcionario
),
    path(
    'historico-mensal/',
    views.historico_mensal
),

    path(
    'exportar-excel/',
    views.exportar_excel_mensal
),
    path(
    'folha-mensal/',
    views.folha_mensal
),

]