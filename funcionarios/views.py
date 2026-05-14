from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import datetime
from django.http import HttpResponse
from openpyxl import Workbook # type: ignore

from .models import Funcionario, Cargo, HoraExtra


# =========================
# HOME
# =========================

def home(request):

    agora = datetime.now()

    meses = [
        '',
        'Janeiro',
        'Fevereiro',
        'Março',
        'Abril',
        'Maio',
        'Junho',
        'Julho',
        'Agosto',
        'Setembro',
        'Outubro',
        'Novembro',
        'Dezembro'
    ]

    mes_atual = meses[agora.month]

    ano_atual = agora.year

    funcionarios = Funcionario.objects.all().order_by('-id')[:10]

    total_funcionarios = Funcionario.objects.count()

    ativos = Funcionario.objects.filter(
        status='ativo'
    ).count()

    inativos = Funcionario.objects.filter(
        status='inativo'
    ).count()

    demitidos = Funcionario.objects.filter(
        status='demitido'
    ).count()

    horas_extras = HoraExtra.objects.count()

    context = {

        'funcionarios': funcionarios,

        'total_funcionarios': total_funcionarios,

        'ativos': ativos,

        'inativos': inativos,

        'demitidos': demitidos,

        'horas_extras': horas_extras,

        'mes_atual': mes_atual,
        'ano_atual': ano_atual,

    }

    return render(
        request,
        'home.html',
        context
    )


# =========================
# CADASTRAR FUNCIONÁRIO
# =========================

def cadastrar_funcionario(request):

    if request.method == 'POST':

        nome = request.POST.get('nome')

        cpf = request.POST.get('cpf')

        carga_horaria = request.POST.get(
            'carga_horaria'
        )

        numero = request.POST.get('numero')

        localidade = request.POST.get(
            'localidade'
        )

        cargo_nome = request.POST.get('cargo')

        data_admissao = request.POST.get(
            'data_admissao'
        )

        cargo = None

        if cargo_nome:

            cargo, created = Cargo.objects.get_or_create(
                nome=cargo_nome
            )

        Funcionario.objects.create(

            nome=nome,

            cpf=cpf,

            carga_horaria=carga_horaria or 0,

            numero=numero,

            localidade=localidade,

            cargo=cargo,

            data_admissao=data_admissao or None,

            status='ativo',

        )

        return redirect('/funcionarios/')

    return render(
        request,
        'funcionario.html'
    )


# =========================
# LISTAR FUNCIONÁRIOS
# =========================

def funcionarios(request):

    busca = request.GET.get('busca')
    ordem = request.GET.get('ordem')

    funcionarios = Funcionario.objects.all()

    if busca:
        funcionarios = funcionarios.filter(
            nome__icontains=busca
        )

    if ordem == 'antigo':
        funcionarios = funcionarios.order_by('id')
    else:
        funcionarios = funcionarios.order_by('-id')

    context = {
        'funcionarios': funcionarios,
        'busca': busca,
        'ordem': ordem,
    }

    return render(
        request,
        'funcionarios.html',
        context
    )


# =========================
# ALTERAR STATUS
# =========================

def alterar_status(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    if request.method == 'POST':

        status = request.POST.get('status')

        if status in [
            'ativo',
            'inativo',
            'demitido'
        ]:

            funcionario.status = status

            funcionario.save()

    return redirect('/funcionarios/')


# =========================
# EDITAR FUNCIONÁRIO
# =========================

def editar_funcionario(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    if request.method == 'POST':

        funcionario.nome = request.POST.get(
            'nome'
        )

        funcionario.cpf = request.POST.get(
            'cpf'
        )

        funcionario.carga_horaria = request.POST.get(
            'carga_horaria'
        ) or 0

        funcionario.numero = request.POST.get(
            'numero'
        )

        funcionario.localidade = request.POST.get(
            'localidade'
        )

        funcionario.data_admissao = request.POST.get(
            'data_admissao'
        ) or None

        cargo_nome = request.POST.get('cargo')

        if cargo_nome:

            cargo, created = Cargo.objects.get_or_create(
                nome=cargo_nome
            )

            funcionario.cargo = cargo

        funcionario.save()

        return redirect('/funcionarios/')

    context = {

        'funcionario': funcionario

    }

    return render(
        request,
        'editar_funcionario.html',
        context
    )


# =========================
# EXCLUIR FUNCIONÁRIO
# =========================

def excluir_funcionario(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    funcionario.delete()

    return redirect('/funcionarios/')


# =========================
# HORAS EXTRAS
# =========================

def horas_extras(request):

    busca = request.GET.get('busca')

    funcionarios = []

    if busca:

        funcionarios = Funcionario.objects.filter(
            nome__icontains=busca
        ).order_by('nome')

    context = {
        'busca': busca,
        'funcionarios': funcionarios,
    }

    return render(
        request,
        'horas_extras.html',
        context
    )


# =========================
# ADICIONAR HORA EXTRA
# =========================

def adicionar_hora_extra(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    if request.method == 'POST':

        tipo = request.POST.get('tipo')

        quantidade_horas = request.POST.get(
            'quantidade_horas'
        )

        valor = request.POST.get('valor')

        mes_referencia = request.POST.get(
            'mes_referencia'
        ) or 1

        ano = request.POST.get(
            'ano'
        ) or 2026

        observacao = request.POST.get(
            'observacao'
        )

        HoraExtra.objects.create(

            funcionario=funcionario,

            tipo=tipo,

            quantidade_horas=quantidade_horas or 0,

            valor=valor or 0,

            mes_referencia=mes_referencia,

            ano=ano,

            observacao=observacao,

        )

        return redirect(
            f'/funcionario/{funcionario.id}/horas/'
        )

    context = {
        'funcionario': funcionario
    }

    return render(
        request,
        'adicionar_hora_extra.html',
        context
    )


# =========================
# RELATÓRIO MENSAL
# =========================

def relatorio_mensal(request):

    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    relatorio = []

    total_horas = 0
    total_valor = 0

    if mes and ano:

        relatorio = HoraExtra.objects.filter(
            mes_referencia=mes,
            ano=ano
        ).select_related(
            'funcionario',
            'funcionario__cargo'
        )

        total_horas = relatorio.aggregate(
            total=Sum('quantidade_horas')
        )['total'] or 0

        total_valor = relatorio.aggregate(
            total=Sum('valor')
        )['total'] or 0

    context = {

        'relatorio': relatorio,

        'mes': mes,
        'ano': ano,

        'total_horas': total_horas,
        'total_valor': total_valor,

    }

    return render(
        request,
        'relatorio_mensal.html',
        context
    )


# =========================
# HORAS DO FUNCIONÁRIO
# =========================

def horas_funcionario(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    lancamentos = HoraExtra.objects.filter(
        funcionario=funcionario
    ).order_by(
        '-ano',
        '-mes_referencia',
        '-id'
    )

    context = {
        'funcionario': funcionario,
        'lancamentos': lancamentos,
    }

    return render(
        request,
        'horas_funcionario.html',
        context
    )


# =========================
# HISTÓRICO MENSAL
# =========================

def historico_mensal(request):

    busca = request.GET.get('busca')
    mes = request.GET.get('mes')

    lancamentos = HoraExtra.objects.all().select_related(
        'funcionario',
        'funcionario__cargo'
    )

    if busca:

        lancamentos = lancamentos.filter(
            funcionario__nome__icontains=busca
        )

    if mes:

        lancamentos = lancamentos.filter(
            mes_referencia=mes
        )

    lancamentos = lancamentos.order_by(
        '-ano',
        '-mes_referencia',
        '-id'
    )

    context = {

        'lancamentos': lancamentos,

        'busca': busca,
        'mes': mes,

    }

    return render(
        request,
        'historico_mensal.html',
        context
    )

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def exportar_excel_mensal(request):

    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    if not mes or not ano:
        return redirect('/relatorio-mensal/')

    lancamentos = HoraExtra.objects.filter(
        mes_referencia=mes,
        ano=ano
    ).select_related(
        'funcionario',
        'funcionario__cargo'
    )

    wb = Workbook()
    ws = wb.active
    ws.title = 'Relatório Mensal'

    cabecalho = [
        'Nome',
        'CPF',
        'Cargo',
        'Status',
        'Tipo',
        'Horas',
        'Valor',
        'Mês',
        'Ano',
        'Observação'
    ]

    ws.append(cabecalho)

    for cell in ws[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='1F4E78')
        cell.alignment = Alignment(horizontal='center')

    total_horas = 0
    total_valor = 0

    for item in lancamentos:

        total_horas += item.quantidade_horas
        total_valor += item.valor

        ws.append([
            item.funcionario.nome,
            item.funcionario.cpf,
            item.funcionario.cargo.nome if item.funcionario.cargo else '',
            item.funcionario.status,
            item.get_tipo_display(),
            float(item.quantidade_horas),
            float(item.valor),
            item.get_mes_referencia_display(),
            item.ano,
            item.observacao or ''
        ])

    

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        row[5].number_format = '0"h"'
        row[6].number_format = 'R$ #,##0.00'

    larguras = {
        'A': 25,
        'B': 18,
        'C': 22,
        'D': 14,
        'E': 22,
        'F': 12,
        'G': 15,
        'H': 15,
        'I': 10,
        'J': 35,
    }

    for coluna, largura in larguras.items():
        ws.column_dimensions[coluna].width = largura

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = f'attachment; filename=relatorio_{mes}_{ano}.xlsx'

    wb.save(response)

    return response


def folha_mensal(request):

    mes = request.GET.get('mes') or request.POST.get('mes')
    ano = request.GET.get('ano') or request.POST.get('ano')

    funcionarios = []

    if request.method == 'POST':

        funcionarios_ids = request.POST.getlist('funcionario_id')

        for funcionario_id in funcionarios_ids:

            horas = request.POST.get(f'horas_{funcionario_id}') or 0
            valor = request.POST.get(f'valor_{funcionario_id}') or 0
            tipo = request.POST.get(f'tipo_{funcionario_id}') or 'normal'
            observacao = request.POST.get(f'observacao_{funcionario_id}')

            if float(horas) > 0 or float(valor) > 0:

                funcionario = get_object_or_404(
                    Funcionario,
                    id=funcionario_id
                )

                HoraExtra.objects.create(
                    funcionario=funcionario,
                    tipo=tipo,
                    quantidade_horas=horas,
                    valor=valor,
                    mes_referencia=mes,
                    ano=ano,
                    observacao=observacao,
                )

        return redirect(
            f'/folha-mensal/?mes={mes}&ano={ano}'
        )

    if mes and ano:

        funcionarios = Funcionario.objects.filter(
            status='ativo'
        ).select_related('cargo')

    context = {
        'funcionarios': funcionarios,
        'mes': mes,
        'ano': ano,
    }

    return render(
        request,
        'folha_mensal.html',
        context
    )