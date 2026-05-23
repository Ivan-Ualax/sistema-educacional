from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from datetime import datetime
from decimal import Decimal

from openpyxl import Workbook # type: ignore
from openpyxl.styles import Font, PatternFill, Alignment # type: ignore

from .models import Funcionario, Cargo, HoraExtra


# HOME

@login_required(login_url='/login/')
def home(request):

    agora = datetime.now()

    perfil, criado = Perfil.objects.get_or_create(
        usuario=request.user
    )

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

    funcionarios = Funcionario.objects.all().order_by('-id')[:10]

    context = {
        'perfil': perfil,
        'funcionarios': funcionarios,
        'total_funcionarios': Funcionario.objects.count(),
        'ativos': Funcionario.objects.filter(status='ativo').count(),
        'inativos': Funcionario.objects.filter(status='inativo').count(),
        'demitidos': Funcionario.objects.filter(status='demitido').count(),
        'horas_extras': HoraExtra.objects.count(),
        'mes_atual': meses[agora.month],
        'ano_atual': agora.year,
    }

    return render(request, 'home.html', context)

@login_required(login_url='/login/')
def cadastrar_funcionario(request):

    if request.method == 'POST':

        cargo_nome = request.POST.get('cargo')

        cargo = None

        if cargo_nome:
            cargo, created = Cargo.objects.get_or_create(
                nome=cargo_nome
            )

        Funcionario.objects.create(
            nome=request.POST.get('nome'),
            cpf=request.POST.get('cpf'),
            escola=request.POST.get('escola'),
            carga_horaria=request.POST.get('carga_horaria') or 0,
            numero=request.POST.get('numero'),
            localidade=request.POST.get('localidade'),
            cargo=cargo,
            data_admissao=request.POST.get('data_admissao') or None,
            status='ativo',
        )

        return redirect('/funcionarios/')

    return render(request, 'funcionario.html')


# LISTAR FUNCIONÁRIOS

@login_required(login_url='/login/')
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

    return render(
        request,
        'funcionarios.html',
        {
            'funcionarios': funcionarios,
            'busca': busca,
            'ordem': ordem,
        }
    )


# ALTERAR STATUS

@login_required(login_url='/login/')
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


# EDITAR FUNCIONÁRIO

@login_required(login_url='/login/')
def editar_funcionario(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    if request.method == 'POST':

        funcionario.nome = request.POST.get('nome')
        funcionario.cpf = request.POST.get('cpf')
        funcionario.escola = request.POST.get('escola')
        funcionario.carga_horaria = request.POST.get('carga_horaria') or 0
        funcionario.numero = request.POST.get('numero')
        funcionario.localidade = request.POST.get('localidade')

        data_admissao = request.POST.get('data_admissao')

        funcionario.data_admissao = data_admissao or None

        cargo_nome = request.POST.get('cargo')

        if cargo_nome:

            cargo, created = Cargo.objects.get_or_create(
                nome=cargo_nome
            )

            funcionario.cargo = cargo

        funcionario.save()

        return redirect('/funcionarios/')

    return render(
        request,
        'editar_funcionario.html',
        {
            'funcionario': funcionario
        }
    )


# EXCLUIR FUNCIONÁRIO

@login_required(login_url='/login/')
def excluir_funcionario(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    funcionario.delete()

    return redirect('/funcionarios/')


# HORAS EXTRAS

@login_required(login_url='/login/')
def horas_extras(request):

    busca = request.GET.get('busca')

    funcionarios = []

    if busca:

        funcionarios = Funcionario.objects.filter(
            nome__icontains=busca
        ).order_by('nome')

    return render(
        request,
        'horas_extras.html',
        {
            'busca': busca,
            'funcionarios': funcionarios,
        }
    )


# ADICIONAR HORA EXTRA

@login_required(login_url='/login/')
def adicionar_hora_extra(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    agora = datetime.now()

    mes_atual = agora.month
    ano_atual = agora.year

    if request.method == 'POST':

        quantidade_horas = request.POST.get(
            'quantidade_horas'
        ) or '0'

        valor = request.POST.get(
            'valor'
        ) or '0'

        quantidade_horas = quantidade_horas.replace(',', '.')
        valor = valor.replace(',', '.')

        HoraExtra.objects.create(
            funcionario=funcionario,
            tipo=request.POST.get('tipo'),
            quantidade_horas=Decimal(quantidade_horas),
            valor=Decimal(valor),
            mes_referencia=request.POST.get('mes_referencia') or mes_atual,
            ano=request.POST.get('ano') or ano_atual,
            observacao=request.POST.get('observacao'),
        )

        return redirect(
            f'/funcionario/{funcionario.id}/horas/'
        )

    return render(
        request,
        'adicionar_hora_extra.html',
        {
            'funcionario': funcionario,
            'mes_atual': mes_atual,
            'ano_atual': ano_atual,
        }
    )


# HORAS DO FUNCIONÁRIO

@login_required(login_url='/login/')
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

    return render(
        request,
        'horas_funcionario.html',
        {
            'funcionario': funcionario,
            'lancamentos': lancamentos,
        }
    )


# LANÇAMENTOS DO MÊS

@login_required(login_url='/login/')
def lancamentos_mes(request):

    agora = datetime.now()

    mes = request.GET.get('mes') or agora.month
    ano = request.GET.get('ano') or agora.year
    busca = request.GET.get('busca')

    lancamentos = HoraExtra.objects.filter(
        mes_referencia=mes,
        ano=ano
    )

    if busca:
        lancamentos = lancamentos.filter(
            funcionario__nome__istartswith=busca
        )

    lancamentos = lancamentos.select_related(
        'funcionario',
        'funcionario__cargo'
    ).order_by(
        'funcionario__nome'
    )

    total_horas = Decimal('0')
    total_valor = Decimal('0')

    controle = {}
    funcionarios_repetidos = []

    for item in lancamentos:

        total_horas += item.quantidade_horas
        total_valor += item.valor

        funcionario_id = item.funcionario.id

        if funcionario_id in controle:
            controle[funcionario_id] += 1
        else:
            controle[funcionario_id] = 1

    for item in lancamentos:

        if controle[item.funcionario.id] > 1:
            funcionarios_repetidos.append(
                item.funcionario.nome
            )

    funcionarios_repetidos = list(set(funcionarios_repetidos))

    return render(
        request,
        'lancamentos_mes.html',
        {
            'lancamentos': lancamentos,
            'mes': int(mes),
            'ano': int(ano),
            'busca': busca,
            'total_horas': total_horas,
            'total_valor': total_valor,
            'funcionarios_repetidos': funcionarios_repetidos,
        }
    )


# EXCLUIR HORA EXTRA

@login_required(login_url='/login/')
def excluir_hora_extra(request, id):

    lancamento = get_object_or_404(
        HoraExtra,
        id=id
    )

    mes = lancamento.mes_referencia
    ano = lancamento.ano

    lancamento.delete()

    return redirect(
        f'/lancamentos-mes/?mes={mes}&ano={ano}'
    )


# EDITAR HORA EXTRA

@login_required(login_url='/login/')
def editar_hora_extra(request, id):

    lancamento = get_object_or_404(
        HoraExtra,
        id=id
    )

    if request.method == 'POST':

        quantidade_horas = request.POST.get(
            'quantidade_horas'
        ) or '0'

        valor = request.POST.get(
            'valor'
        ) or '0'

        quantidade_horas = quantidade_horas.replace(',', '.')
        valor = valor.replace(',', '.')

        lancamento.tipo = request.POST.get('tipo')

        lancamento.quantidade_horas = Decimal(
            quantidade_horas
        )

        lancamento.valor = Decimal(
            valor
        )

        lancamento.mes_referencia = request.POST.get(
            'mes_referencia'
        )

        lancamento.ano = request.POST.get('ano')

        lancamento.observacao = request.POST.get(
            'observacao'
        )

        lancamento.save()

        return redirect(
            f'/funcionario/{lancamento.funcionario.id}/horas/'
        )

    return render(
        request,
        'editar_hora_extra.html',
        {
            'lancamento': lancamento
        }
    )


# EXPORTAR EXCEL

@login_required(login_url='/login/')
def exportar_lancamentos_excel(request):

    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    if not mes or not ano:

        return redirect('/lancamentos-mes/')

    lancamentos = HoraExtra.objects.filter(
        mes_referencia=mes,
        ano=ano
    ).select_related(
        'funcionario',
        'funcionario__cargo'
    ).order_by(
        'funcionario__nome'
    )

    wb = Workbook()

    ws = wb.active

    ws.title = 'Horas Extras'

    ws.append([
        'Funcionário',
        'CPF',
        'Escola',
        'Cargo',
        'Carga Horária',
        'Contato',
        'Localidade',
        'Status',
        'Tipo',
        'Horas',
        'Valor',
        'Mês',
        'Ano',
        'Observação'
    ])

    # CABEÇALHO

    for cell in ws[1]:

        cell.font = Font(
            bold=True,
            color='FFFFFF',
            size=12
        )

        cell.fill = PatternFill(
            'solid',
            fgColor='1F4E78'
        )

        cell.alignment = Alignment(
            horizontal='center',
            vertical='center'
        )

    # DADOS

    for item in lancamentos:

        ws.append([
            item.funcionario.nome,
            item.funcionario.cpf or '',
            item.funcionario.escola or '',
            item.funcionario.cargo.nome if item.funcionario.cargo else '',
            item.funcionario.carga_horaria,
            item.funcionario.numero or '',
            item.funcionario.localidade or '',
            item.funcionario.status,
            item.get_tipo_display(),
            f'{float(item.quantidade_horas):,.0f}h',
            f'R$ {float(item.valor):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            item.get_mes_referencia_display(),
            item.ano,
            item.observacao or ''
        ])

    # AJUSTAR LARGURA DAS COLUNAS

    larguras = {
        'A': 20,
        'B': 15,
        'C': 10,
        'D': 10,
        'E': 10,
        'F': 10,
        'G': 15,
        'H': 10,
        'I': 10,
        'J': 10,
        'K': 15,
        'L': 10,
        'M': 12,
        'N': 20,
    }

    for coluna, largura in larguras.items():

        ws.column_dimensions[coluna].width = largura

    # ALINHAMENTO E TEXTO

    for row in ws.iter_rows():

        for cell in row:

            cell.alignment = Alignment(
                vertical='center',
                wrap_text=True
            )

    # ALTURA DAS LINHAS

    for row in ws.iter_rows(min_row=2):

        ws.row_dimensions[row[0].row].height = 28

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        f'attachment; filename=horas_extras_{mes}_{ano}.xlsx'
    )

    wb.save(response)

    return response

