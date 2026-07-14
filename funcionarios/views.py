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
from django.db.models import Q
from django.db.models import Count

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

def usuario_pode_ver_valores(user):

    return user.is_superuser


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

    escolas_resumo = (
    Funcionario.objects
    .exclude(escola__isnull=True)
    .exclude(escola='')
    .annotate(escola_limpa=Trim('escola'))
    .values('escola_limpa')
    .annotate(total=Count('id'))
    .order_by('escola_limpa')
)

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

    'escolas_resumo': escolas_resumo,

}

    return render(
        request,
        'home.html',
        context
    )


@login_required(login_url='/login/')
def cadastrar_funcionario(request):

    escolas = (
        Funcionario.objects
        .exclude(escola__isnull=True)
        .exclude(escola='')
        .annotate(escola_limpa=Trim('escola'))
        .values_list('escola_limpa', flat=True)
        .distinct()
        .order_by('escola_limpa')
    )

    if request.method == 'POST':

        escola_existente = request.POST.get('escola_existente')
        nova_escola = request.POST.get('nova_escola')

        escola = nova_escola.strip() if nova_escola else escola_existente

        cargo_nome = request.POST.get('cargo')

        cargo = None

        if cargo_nome:

            cargo, created = Cargo.objects.get_or_create(
                nome=cargo_nome.strip()
            )

        Funcionario.objects.create(

            nome=request.POST.get('nome'),

            situacao_contratual=request.POST.get(
                'situacao_contratual'
            ),

            cpf=request.POST.get('cpf'),

            escola=escola,

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
        'funcionario.html',
        {
            'escolas': escolas
        }
    )


from django.db.models import Count

@login_required(login_url='/login/')
def funcionarios(request):

    busca = request.GET.get('busca')

    ordem = request.GET.get('ordem')

    escola_filtro = request.GET.get('escola') or ''

    funcionarios = Funcionario.objects.all()

    if busca:

        funcionarios = funcionarios.filter(
            nome__icontains=busca
        )

    if escola_filtro:

        funcionarios = funcionarios.annotate(
            escola_limpa=Trim('escola')
        ).filter(
            escola_limpa=escola_filtro.strip()
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


    escolas = (
    Funcionario.objects
    .exclude(escola__isnull=True)
    .exclude(escola='')
    .annotate(escola_limpa=Trim('escola'))
    .values_list('escola_limpa', flat=True)
    .distinct()
    .order_by('escola_limpa')
)
    return render(
        request,
        'funcionarios.html',
        {
            'funcionarios': funcionarios,
            'busca': busca,
            'ordem': ordem,
            'nomes_duplicados': nomes_duplicados,
            'escolas': escolas,
            'escola_filtro': escola_filtro,
        }
    )


@login_required(login_url='/login/')
def alterar_status(request, id):

    funcionario = get_object_or_404(
        Funcionario,
        id=id
    )

    escolas = (
    Funcionario.objects
    .exclude(escola__isnull=True)
    .exclude(escola='')
    .annotate(escola_limpa=Trim('escola'))
    .values_list('escola_limpa', flat=True)
    .distinct()
    .order_by('escola_limpa')
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

    escolas = (
        Funcionario.objects
        .exclude(escola__isnull=True)
        .exclude(escola='')
        .annotate(escola_limpa=Trim('escola'))
        .values_list('escola_limpa', flat=True)
        .distinct()
        .order_by('escola_limpa')
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
                    'nome_duplicado': nome,
                    'escolas': escolas,
                }
            )

        funcionario.nome = nome
        funcionario.situacao_contratual = request.POST.get('situacao_contratual')
        funcionario.cpf = request.POST.get('cpf')

        escola_existente = request.POST.get('escola_existente')
        nova_escola = request.POST.get('nova_escola')

        if nova_escola:
            funcionario.escola = nova_escola.strip()
        elif escola_existente:
            funcionario.escola = escola_existente

        funcionario.carga_horaria = request.POST.get('carga_horaria') or 0
        funcionario.numero = request.POST.get('numero')
        funcionario.localidade = request.POST.get('localidade')
        funcionario.data_admissao = request.POST.get('data_admissao') or None

        cargo_nome = request.POST.get('cargo')

        if cargo_nome:
            cargo, created = Cargo.objects.get_or_create(
                nome=cargo_nome.strip()
            )
            funcionario.cargo = cargo

        funcionario.save()

        return redirect('/funcionarios/')

    return render(
        request,
        'editar_funcionario.html',
        {
            'funcionario': funcionario,
            'escolas': escolas,
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
        'pode_ver_valores': usuario_pode_ver_valores(request.user),
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
            
            'pode_ver_valores': usuario_pode_ver_valores(request.user),
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
        'lancamento': lancamento,
        'pode_ver_valores': usuario_pode_ver_valores(request.user),
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
    busca = request.GET.get('busca') or ''
    escola_filtro = request.GET.get('escola') or ''

    if not mes or not ano:
        return redirect('/lancamentos-mes/')

    pode_ver_valores = usuario_pode_ver_valores(request.user)

    lancamentos = HoraExtra.objects.filter(
        mes_referencia=mes,
        ano=ano
    ).select_related(
        'funcionario',
        'funcionario__cargo'
    )

    if busca:
        lancamentos = lancamentos.filter(
            funcionario__nome__icontains=busca.strip()
        )

    if escola_filtro:
        lancamentos = lancamentos.annotate(
            escola_limpa=Trim('funcionario__escola')
        ).filter(
            escola_limpa=escola_filtro.strip()
        )

    lancamentos = lancamentos.order_by(
    '-data_falta',
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

    titulo_texto = f'FOLHA-MÊS DE {meses.get(str(mes), mes)} {ano}'

    if escola_filtro:
        titulo_texto += f' - {escola_filtro.strip()}'

    titulo = ws['A1']
    titulo.value = titulo_texto
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

            if pode_ver_valores:
                texto_hora = (
                    f'{item.get_tipo_display()} | '
                    f'Horas: {int(item.quantidade_horas)}h | '
                    f'Valor: R$ {item.valor} | '
                    f'Obs: {item.observacao_hora_extra or "Sem observação"}'
                )
            else:
                texto_hora = (
                    f'{item.get_tipo_display()} | '
                    f'Horas: {int(item.quantidade_horas)}h | '
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
            pendencia = 'Sem pendência'

        ws.append([
            item.funcionario.nome,
            item.funcionario.cargo.nome if item.funcionario.cargo else '',
            (item.funcionario.escola or '').strip(),
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

    nome_arquivo = f'pendencias_{mes}_{ano}'

    if escola_filtro:
        nome_arquivo += f'_{escola_filtro.strip().replace(" ", "_")}'

    response['Content-Disposition'] = (
        f'attachment; filename={nome_arquivo}.xlsx'
    )

    wb.save(response)

    return response
@login_required(login_url='/login/')
def lancamentos_mes(request):

    agora = datetime.now()

    mes = request.GET.get('mes') or agora.month
    ano = request.GET.get('ano') or agora.year
    busca = request.GET.get('busca') or ''
    escola_filtro = request.GET.get('escola') or ''

    lancamentos = HoraExtra.objects.filter(
        mes_referencia=mes,
        ano=ano
    ).select_related(
        'funcionario',
        'funcionario__cargo'
    )

    if busca:
        lancamentos = lancamentos.filter(
            funcionario__nome__icontains=busca.strip()
        )

    if escola_filtro:
        lancamentos = lancamentos.annotate(
            escola_limpa=Trim('funcionario__escola')
        ).filter(
            escola_limpa=escola_filtro.strip()
        )

    lancamentos = lancamentos.order_by(
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

    escolas = (
        Funcionario.objects
        .exclude(escola__isnull=True)
        .exclude(escola='')
        .annotate(escola_limpa=Trim('escola'))
        .values_list('escola_limpa', flat=True)
        .distinct()
        .order_by('escola_limpa')
    )

    return render(
        request,
        'lancamentos_mes.html',
        {
            'lancamentos': lancamentos,
            'mes': int(mes),
            'ano': int(ano),
            'busca': busca,
            'escolas': escolas,
            'escola_filtro': escola_filtro,
            'total_horas': total_horas,
            'total_valor': total_valor,
            'mes_encerrado': mes_encerrado,

             'pode_ver_valores': usuario_pode_ver_valores(request.user),
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
    escola_filtro = request.GET.get('escola') or ''

    lancamentos = HoraExtra.objects.none()

    if mes and ano:
        lancamentos = HoraExtra.objects.filter(
            encerrado=True,
            mes_referencia=mes,
            ano=ano
        ).select_related(
            'funcionario',
            'funcionario__cargo'
        )

        if escola_filtro:
            lancamentos = lancamentos.annotate(
                escola_limpa=Trim('funcionario__escola')
            ).filter(
                escola_limpa=escola_filtro.strip()
            )

        lancamentos = lancamentos.order_by(
            'funcionario__nome'
        )

    escolas = (
        Funcionario.objects
        .exclude(escola__isnull=True)
        .exclude(escola='')
        .annotate(escola_limpa=Trim('escola'))
        .values_list('escola_limpa', flat=True)
        .distinct()
        .order_by('escola_limpa')
    )

    return render(
        request,
        'lancamentos_gerais.html',
        {
            'lancamentos': lancamentos,
            'mes': int(mes) if mes else '',
            'ano': int(ano) if ano else '',
            'escolas': escolas,
            'escola_filtro': escola_filtro,
        }
    )


@login_required(login_url='/login/')
def exportar_funcionarios_excel(request):

    busca = request.GET.get('busca') or ''
    escola_filtro = request.GET.get('escola') or ''
    ordem = request.GET.get('ordem') or ''

    funcionarios = (
        Funcionario.objects
        .select_related('cargo')
        .all()
    )

    if busca:
        funcionarios = funcionarios.filter(
            nome__icontains=busca.strip()
        )

    if escola_filtro:
        funcionarios = funcionarios.annotate(
            escola_limpa=Trim('escola')
        ).filter(
            escola_limpa=escola_filtro.strip()
        )

    if ordem == 'antigo':
        funcionarios = funcionarios.order_by('id')
    else:
        funcionarios = funcionarios.order_by('-id')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Funcionários'

    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    ws.page_margins = PageMargins(
        left=0.20,
        right=0.20,
        top=0.30,
        bottom=0.30,
        header=0,
        footer=0
    )

    # Título
    ws.merge_cells('A1:J1')

    titulo = ws['A1']
    titulo.value = 'RELAÇÃO DE FUNCIONÁRIOS'
    titulo.font = Font(
        bold=True,
        color='FFFFFF',
        size=14
    )
    titulo.fill = PatternFill(
        'solid',
        fgColor='1F4E78'
    )
    titulo.alignment = Alignment(
        horizontal='center',
        vertical='center'
    )

    # Descrição dos filtros aplicados
    filtros_aplicados = []

    if busca:
        filtros_aplicados.append(
            f'Nome: {busca}'
        )

    if escola_filtro:
        filtros_aplicados.append(
            f'Escola: {escola_filtro}'
        )

    texto_filtros = (
        'Filtros: ' + ' | '.join(filtros_aplicados)
        if filtros_aplicados
        else 'Todos os funcionários'
    )

    ws.merge_cells('A2:J2')

    ws['A2'] = texto_filtros
    ws['A2'].font = Font(
        italic=True,
        color='475569',
        size=10
    )
    ws['A2'].alignment = Alignment(
        horizontal='center',
        vertical='center'
    )

    cabecalhos = [
        'NOME',
        'SITUAÇÃO CONTRATUAL',
        'CPF',
        'NÚMERO',
        'LOCALIDADE',
        'ESCOLA',
        'CARGO',
        'CARGA HORÁRIA',
        'STATUS',
        'DATA DE ADMISSÃO',
    ]

    ws.append(cabecalhos)

    borda = Border(
        left=Side(style='thin', color='94A3B8'),
        right=Side(style='thin', color='94A3B8'),
        top=Side(style='thin', color='94A3B8'),
        bottom=Side(style='thin', color='94A3B8')
    )

    for cell in ws[3]:
        cell.font = Font(
            bold=True,
            color='FFFFFF',
            size=9
        )
        cell.fill = PatternFill(
            'solid',
            fgColor='244062'
        )
        cell.alignment = Alignment(
            horizontal='center',
            vertical='center',
            wrap_text=True
        )
        cell.border = borda

    for funcionario in funcionarios:

        data_admissao = (
            funcionario.data_admissao.strftime('%d/%m/%Y')
            if funcionario.data_admissao
            else ''
        )

        ws.append([
            funcionario.nome,
            funcionario.situacao_contratual or '',
            funcionario.cpf or '',
            funcionario.numero or '',
            funcionario.localidade or '',
            (funcionario.escola or '').strip(),
            funcionario.cargo.nome if funcionario.cargo else '',
            funcionario.carga_horaria or 0,
            funcionario.get_status_display(),
            data_admissao,
        ])

        linha = ws.max_row

        for cell in ws[linha]:
            cell.font = Font(size=9)
            cell.border = borda
            cell.alignment = Alignment(
                vertical='center',
                wrap_text=True
            )

        ws.cell(
            row=linha,
            column=8
        ).number_format = '0" h"'

    ws.column_dimensions['A'].width = 32
    ws.column_dimensions['B'].width = 22
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 16
    ws.column_dimensions['E'].width = 25
    ws.column_dimensions['F'].width = 35
    ws.column_dimensions['G'].width = 25
    ws.column_dimensions['H'].width = 16
    ws.column_dimensions['I'].width = 15
    ws.column_dimensions['J'].width = 18

    ws.row_dimensions[1].height = 24
    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 28

    for linha in range(4, ws.max_row + 1):
        ws.row_dimensions[linha].height = 24

    ws.freeze_panes = 'A4'

    if ws.max_row >= 4:
        ws.auto_filter.ref = f'A3:J{ws.max_row}'

    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-'
            'officedocument.spreadsheetml.sheet'
        )
    )

    data_atual = timezone.localdate().strftime('%d-%m-%Y')

    response['Content-Disposition'] = (
        f'attachment; '
        f'filename="funcionarios_{data_atual}.xlsx"'
    )

    wb.save(response)

    return response