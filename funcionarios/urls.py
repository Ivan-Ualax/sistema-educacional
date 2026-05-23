from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # HOME
    # =========================

    path(
        '',
        views.home,
        name='home'
    ),

    # =========================
    # CADASTRAR FUNCIONÁRIO
    # =========================

    path(
        'funcionarios/cadastrar/',
        views.cadastrar_funcionario,
        name='cadastrar_funcionario'
    ),

    # =========================
    # LISTAR FUNCIONÁRIOS
    # =========================

    path(
        'funcionarios/',
        views.funcionarios,
        name='funcionarios'
    ),

    # =========================
    # ALTERAR STATUS
    # =========================

    path(
        'funcionarios/status/<int:id>/',
        views.alterar_status,
        name='alterar_status'
    ),

    # =========================
    # EDITAR FUNCIONÁRIO
    # =========================

    path(
        'funcionarios/editar/<int:id>/',
        views.editar_funcionario,
        name='editar_funcionario'
    ),

    # =========================
    # EXCLUIR FUNCIONÁRIO
    # =========================

    path(
        'funcionarios/excluir/<int:id>/',
        views.excluir_funcionario,
        name='excluir_funcionario'
    ),

    # =========================
    # HORAS EXTRAS
    # =========================

    path(
        'horas-extras/',
        views.horas_extras,
        name='horas_extras'
    ),

    path(
        'horas-extras/adicionar/<int:id>/',
        views.adicionar_hora_extra,
        name='adicionar_hora_extra'
    ),

    path(
        'funcionario/<int:id>/horas/',
        views.horas_funcionario,
        name='horas_funcionario'
    ),

    # =========================
    # LANÇAMENTOS DO MÊS
    # =========================

    path(
        'lancamentos-mes/',
        views.lancamentos_mes,
        name='lancamentos_mes'
    ),

    # =========================
    # EDITAR HORA EXTRA
    # =========================

    path(
        'horas-extras/editar/<int:id>/',
        views.editar_hora_extra,
        name='editar_hora_extra'
    ),

    # =========================
    # EXCLUIR HORA EXTRA
    # =========================

    path(
        'horas-extras/excluir/<int:id>/',
        views.excluir_hora_extra,
        name='excluir_hora_extra'
    ),

    # =========================
    # EXPORTAR EXCEL
    # =========================

    path(
        'exportar-lancamentos-excel/',
        views.exportar_lancamentos_excel,
        name='exportar_lancamentos_excel'
    ),

    

]