from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'contratos/',
        views.listar_contratos,
        name='listar_contratos'
    ),

    path(
        'contratos/cadastrar/',
        views.cadastrar_contrato,
        name='cadastrar_contrato'
    ),

    path(
        'contratos/categoria/<str:modalidade>/<str:secretaria>/',
        views.contratos_por_categoria,
        name='contratos_por_categoria'
    ),

    path(
        'contratos/<int:id>/',
        views.detalhe_contrato,
        name='detalhe_contrato'
    ),

    path(
        'contratos/<int:id>/editar/',
        views.editar_contrato,
        name='editar_contrato'
    ),

    path(
        'contratos/<int:id>/situacao/',
        views.alterar_situacao,
        name='alterar_situacao'
    ),

    path(
        'contratos/<int:id>/excluir/',
        views.excluir_contrato,
        name='excluir_contrato'
    ),

    path(
        'relatorios/',
        views.relatorios,
        name='relatorios'
    ),

    path(
        'relatorios/exportar-excel/',
        views.exportar_contratos_excel,
        name='exportar_contratos_excel'
    ),
]