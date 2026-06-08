from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from datetime import datetime
from decimal import Decimal
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.styles import Border, Side
from openpyxl.worksheet.page import PageMargins
from django.db.models.functions import Lower, Trim

from .models import Funcionario, Cargo, HoraExtra


def tratar_data_falta(data_falta):

    if not data_falta:
        return None

    try:

        data_completa = f'{data_falta}/2026'

        return datetime.strptime(
            data_completa,
            '%d/%m/%Y'
        ).date()

    except:

        return None


def limpar_observacao(texto):

    texto = texto or ''

    linhas_limpas = []

    for linha in texto.splitlines():

        linha = linha.strip()

        if linha.lower() == 'none':
            continue

        if linha:
            linhas_limpas.append(linha)

    return '\n'.join(linhas_limpas)


@login_required(login_url='/login/')
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

    funcionarios = Funcionario.objects.all().order_by('-id')[:10]

    context = {

        'funcionarios': funcionarios,

        'total_funcionarios': Funcionario.objects.count(),

        'ativos': Funcionario.objects.filter(
            status='ativo'
        ).count(),

        'inativos': Funcionario.objects.filter(
            status='inativo'
        ).count(),

        'demitidos': Funcionario.objects.filter(
            status='demitido'
        ).count(),

        'horas_extras': HoraExtra.objects.count(),

        'mes_atual': meses[agora.month],

        'ano_atual': agora.year,

    }

    return render(
        request,
        'home.html',
        context
    )


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

            situacao_contratual=request.POST.get(
                'situacao_contratual'
            ),

            cpf=request.POST.get('cpf'),

            escola=request.POST.get('escola'),

            carga_horaria=request.POST.get(
                'carga_horaria'
            ) or 0,

            numero=request.POST.get('numero'),

            localidade=request.POST.get('localidade'),

            cargo=cargo,

            data_admissao=request.POST.get(
                'data_admissao'
            ) or None,

            status='ativo',

        )

        return redirect('/funcionarios/')

    return render(
        request,
        'funcionario.html'
    )


from django.db.models import Count

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

    nomes_duplicados = (
    Funcionario.objects
    .annotate(nome_limpo=Lower(Trim('nome')))
    .values('nome_limpo')
    .annotate(total=Count('id'))
    .filter(total__gt=1)
)

    return render(
        request,
        'funcionarios.html',
        {
            'funcionarios': funcionarios,
            'busca': busca,
            'ordem': ordem,
            'nomes_duplicados': nomes_duplicados,
        }
    )


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


@login_required(login_url='/login/')
def editar_funcionario(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    if request.method == 'POST':

        nome = request.POST.get('nome')

        nome_duplicado = Funcionario.objects.filter(
            nome__iexact=nome
        ).exclude(
            id=funcionario.id
        ).first()

        if nome_duplicado:

            return render(
                request,
                'editar_funcionario.html',
                {
                    'funcionario': funcionario,
                    'erro_nome_duplicado': True,
                    'nome_duplicado': nome
                }
            )

        funcionario.nome = nome

        funcionario.situacao_contratual = request.POST.get(
            'situacao_contratual'
        )

        funcionario.cpf = request.POST.get('cpf')

        funcionario.escola = request.POST.get(
            'escola'
        ) or funcionario.escola

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

    return render(
        request,
        'editar_funcionario.html',
        {
            'funcionario': funcionario
        }
    )


@login_required(login_url='/login/')
def excluir_funcionario(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    funcionario.delete()

    return redirect('/funcionarios/')


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


@login_required(login_url='/login/')
def adicionar_hora_extra(request, id):

    funcionario = get_object_or_404(Funcionario, id=id)

    agora = datetime.now()
    mes_atual = agora.month
    ano_atual = agora.year

    if request.method == 'POST':

        quantidade_horas = request.POST.get('quantidade_horas') or '0'
        valor = request.POST.get('valor') or '0'

        quantidade_horas = quantidade_horas.replace('h', '').replace('H', '').replace('R$', '').replace(' ', '').replace(',', '.')
        valor = valor.replace('h', '').replace('H', '').replace('R$', '').replace(' ', '').replace(',', '.')

        mes_referencia = request.POST.get('mes_referencia') or mes_atual
        ano = request.POST.get('ano') or ano_atual

        lancamento, criado = HoraExtra.objects.get_or_create(
            funcionario=funcionario,
            mes_referencia=mes_referencia,
            ano=ano,
            defaults={
                'tipo': request.POST.get('tipo') or 'normal',
                'quantidade_horas': 0,
                'valor': 0,
                'observacao_hora_extra': '',
                'numero_faltas': 0,
                'data_falta': None,
                'observacao_falta': '',
                'cor_texto': 'normal',
            }
        )

        lancamento.tipo = request.POST.get('tipo') or 'normal'

        try:
            quantidade_horas_decimal = Decimal(quantidade_horas)
        except:
            quantidade_horas_decimal = Decimal('0')

        try:
            valor_decimal = Decimal(valor)
        except:
            valor_decimal = Decimal('0')

        lancamento.quantidade_horas = Decimal(lancamento.quantidade_horas or 0) + quantidade_horas_decimal
        lancamento.valor = Decimal(lancamento.valor or 0) + valor_decimal

        nova_obs_hora = limpar_observacao(request.POST.get('observacao'))

        if nova_obs_hora:
            obs_antiga_hora = limpar_observacao(lancamento.observacao_hora_extra)
            lancamento.observacao_hora_extra = (
                obs_antiga_hora + '\n' + nova_obs_hora
                if obs_antiga_hora else nova_obs_hora
            )

        numero_faltas = int(request.POST.get('numero_faltas') or 0)
        lancamento.numero_faltas = int(lancamento.numero_faltas or 0) + numero_faltas

        data_falta = tratar_data_falta(request.POST.get('data_falta'))

        if data_falta:
            lancamento.data_falta = data_falta

        nova_obs_falta = limpar_observacao(request.POST.get('observacao_falta'))

        if nova_obs_falta:
            obs_antiga_falta = limpar_observacao(lancamento.observacao_falta)
            lancamento.observacao_falta = (
                obs_antiga_falta + '\n' + nova_obs_falta
                if obs_antiga_falta else nova_obs_falta
            )

        lancamento.cor_texto = request.POST.get('cor_texto') or 'normal'

        lancamento.save()

        return redirect(f'/funcionario/{funcionario.id}/horas/')

    return render(
        request,
        'adicionar_hora_extra.html',
        {
            'funcionario': funcionario,
            'mes_atual': mes_atual,
            'ano_atual': ano_atual,
        }
    )

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

        quantidade_horas = quantidade_horas.replace(
            ',',
            '.'
        )

        valor = valor.replace(
            ',',
            '.'
        )

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

        lancamento.ano = request.POST.get(
            'ano'
        )

        lancamento.observacao_hora_extra = limpar_observacao(
            request.POST.get(
                'observacao_hora_extra'
            )
        )

        lancamento.numero_faltas = request.POST.get(
            'numero_faltas'
        ) or 0

        lancamento.data_falta = tratar_data_falta(
            request.POST.get('data_falta')
        )

        lancamento.observacao_falta = limpar_observacao(
            request.POST.get(
                'observacao_falta'
            )
        )

        lancamento.cor_texto = request.POST.get(
            'cor_texto'
        ) or 'normal'

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


@login_required(login_url='/login/')
def excluir_hora_extra(request, id):

    try:
        lancamento = HoraExtra.objects.get(id=id)
    except HoraExtra.DoesNotExist:
        return redirect('/lancamentos-mes/')

    mes = lancamento.mes_referencia
    ano = lancamento.ano

    if lancamento.encerrado:
        return redirect(
            f'/lancamentos-mes/?mes={mes}&ano={ano}'
        )

    lancamento.delete()

    return redirect(
        f'/lancamentos-mes/?mes={mes}&ano={ano}'
    )

@login_required(login_url='/login/')
def exportar_pendencias_excel(request):

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
    ws.title = 'Pendências'

    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    ws.print_options.horizontalCentered = True

    ws.page_margins = PageMargins(
        left=0.15,
        right=0.15,
        top=0.05,
        bottom=0.15,
        header=0,
        footer=0
    )

    ws.merge_cells('A1:D1')

    titulo = ws['A1']
    meses = {
    '1': 'JANEIRO',
    '2': 'FEVEREIRO',
    '3': 'MARÇO',
    '4': 'ABRIL',
    '5': 'MAIO',
    '6': 'JUNHO',
    '7': 'JULHO',
    '8': 'AGOSTO',
    '9': 'SETEMBRO',
    '10': 'OUTUBRO',
    '11': 'NOVEMBRO',
    '12': 'DEZEMBRO',
}

    titulo.value = f'FOLHA-MÊS DE {meses.get(str(mes), mes)} {ano}'
    titulo.font = Font(bold=True, color='FFFFFF', size=13)
    titulo.fill = PatternFill('solid', fgColor='1F4E78')
    titulo.alignment = Alignment(horizontal='center', vertical='center')

    ws.append([
        'FUNCIONÁRIO',
        'FUNÇÃO',
        'LOCAL DE TRABALHO',
        'PENDÊNCIA'
    ])

    borda = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for cell in ws[2]:
        cell.font = Font(bold=True, color='FFFFFF', size=9)
        cell.fill = PatternFill('solid', fgColor='244062')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = borda

    for item in lancamentos:

        pendencias = []

        if item.quantidade_horas and item.quantidade_horas > 0:
            texto_hora = (
                f'{item.get_tipo_display()} | '
                f'Horas: {int(item.quantidade_horas)}h | '
                f'Valor: R$ {item.valor} | '
                f'Obs: {item.observacao_hora_extra or "Sem observação"}'
            )
            pendencias.append(texto_hora)

        if item.numero_faltas and item.numero_faltas > 0:
            data_falta = (
                item.data_falta.strftime('%d/%m/%Y')
                if item.data_falta else
                'Não informada'
            )

            texto_falta = (
                f'Faltas: {item.numero_faltas} | '
                f'Data: {data_falta} | '
                f'Obs: {item.observacao_falta or "Sem observação"}'
            )
            pendencias.append(texto_falta)

        pendencia = ' || '.join(pendencias)

        if not pendencia:
            continue

        ws.append([
            item.funcionario.nome,
            item.funcionario.cargo.nome if item.funcionario.cargo else '',
            item.funcionario.escola or '',
            pendencia
        ])

        for cell in ws[ws.max_row]:
            cell.font = Font(size=9)
            cell.border = borda
            cell.alignment = Alignment(
                horizontal='center',
                vertical='center',
                wrap_text=True
            )

    ws.column_dimensions['A'].width = 34
    ws.column_dimensions['B'].width = 24
    ws.column_dimensions['C'].width = 34
    ws.column_dimensions['D'].width = 65

    ws.row_dimensions[1].height = 18
    ws.row_dimensions[2].height = 15

    for linha in range(3, ws.max_row + 1):
        ws.row_dimensions[linha].height = 22

    ws.freeze_panes = 'A3'

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        f'attachment; filename=pendencias_{mes}_{ano}.xlsx'
    )

    wb.save(response)

    return response
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

    for item in lancamentos:
        total_horas += item.quantidade_horas
        total_valor += item.valor

    mes_encerrado = lancamentos.filter(
        encerrado=True
    ).exists()

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
            'mes_encerrado': mes_encerrado,
        }
    )

@login_required(login_url='/login/')
def encerrar_lancamentos_mes(request):

    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    if not mes or not ano:
        return redirect('/lancamentos-mes/')

    HoraExtra.objects.filter(
        mes_referencia=mes,
        ano=ano,
        encerrado=False
    ).update(
        encerrado=True,
        data_encerramento=timezone.now()
    )

    return redirect('/lancamentos-gerais/')


@login_required(login_url='/login/')
def lancamentos_gerais(request):

    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    lancamentos = HoraExtra.objects.none()

    if mes and ano:
        lancamentos = HoraExtra.objects.filter(
            encerrado=True,
            mes_referencia=mes,
            ano=ano
        ).select_related(
            'funcionario',
            'funcionario__cargo'
        ).order_by(
            'funcionario__nome'
        )

    return render(
        request,
        'lancamentos_gerais.html',
        {
            'lancamentos': lancamentos,
            'mes': int(mes) if mes else '',
            'ano': int(ano) if ano else '',
        }
    )