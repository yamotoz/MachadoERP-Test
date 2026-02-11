# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from datetime import datetime
from dateutil.relativedelta import relativedelta


class DashboardCombustivelController(http.Controller):
    """
    Controller para o Dashboard de Combustível.
    Prepara e fornece os dados para o template QWeb.
    """

    @http.route('/combustivel/dashboard', type='http', auth='user', website=False)
    def dashboard(self, **kw):
        """
        Renderiza o dashboard de combustível com dados agregados.
        """
        # Verificar permissão
        if not request.env.user.has_group('controle_combustivel.group_analista'):
            return request.redirect('/web')
        
        # Buscar tanque
        Tanque = request.env['controle.combustivel.tanque']
        tanque = Tanque.search([], limit=1)
        
        if not tanque:
            tanque = Tanque.create({
                'name': 'Tanque Principal',
                'capacidade': 6000.0,
            })
        
        # Calcular período do mês atual
        hoje = fields.Date.today()
        primeiro_dia_mes = hoje.replace(day=1)
        ultimo_dia_mes = (primeiro_dia_mes + relativedelta(months=1)) - relativedelta(days=1)
        
        # Buscar abastecimentos do mês
        Abastecimento = request.env['controle.combustivel.abastecimento']
        abastecimentos_mes = Abastecimento.search([
            ('data_hora', '>=', datetime.combine(primeiro_dia_mes, datetime.min.time())),
            ('data_hora', '<=', datetime.combine(ultimo_dia_mes, datetime.max.time())),
            ('state', '=', 'confirmado'),
        ])
        
        # Calcular totais
        consumo_litros = sum(abastecimentos_mes.mapped('quantidade_litros'))
        consumo_valor = sum(abastecimentos_mes.mapped('total'))
        total_abastecimentos = len(abastecimentos_mes)
        
        # Buscar último abastecimento
        ultimo_abastecimento = Abastecimento.search([
            ('state', '=', 'confirmado'),
        ], order='data_hora desc', limit=1)
        
        # Definir cores baseado no nível
        percentual = tanque.percentual_nivel if tanque else 0
        if percentual > 50:
            cor_badge = 'bg-success'
            cor_progress = 'bg-success'
            cor_tank = 'tank-green'
        elif percentual >= 20:
            cor_badge = 'bg-warning'
            cor_progress = 'bg-warning'
            cor_tank = 'tank-yellow'
        else:
            cor_badge = 'bg-danger'
            cor_progress = 'bg-danger'
            cor_tank = 'tank-red'
        
        # Calcular consumo dos últimos 7 dias para gráfico simples
        consumo_diario = []
        for i in range(6, -1, -1):
            dia = hoje - relativedelta(days=i)
            litros_dia = sum(Abastecimento.search([
                ('data_hora', '>=', datetime.combine(dia, datetime.min.time())),
                ('data_hora', '<=', datetime.combine(dia, datetime.max.time())),
                ('state', '=', 'confirmado'),
            ]).mapped('quantidade_litros'))
            consumo_diario.append({
                'dia': dia.strftime('%d/%m'),
                'litros': litros_dia,
                'altura': min(100, (litros_dia / (consumo_litros/len(abastecimentos_mes) * 3 if total_abastecimentos > 0 else 100)) * 100) if total_abastecimentos > 0 else 0
            })

        # Formatar período
        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        periodo_mes = f"{meses_pt[hoje.month]}/{hoje.year}"

        # Preparar dados para o template
        values = {
            'tanque': tanque,
            'consumo_litros': consumo_litros,
            'consumo_valor': consumo_valor,
            'total_abastecimentos': total_abastecimentos,
            'ultimo_abastecimento': ultimo_abastecimento,
            'periodo_mes': periodo_mes,
            'data_atualizacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'cor_badge': cor_badge,
            'cor_progress': cor_progress,
            'cor_tank': cor_tank,
            'action_abastecimento': request.env.ref('controle_combustivel.action_abastecimento_tree').id,
            'consumo_diario': consumo_diario,
        }
        
        return request.render(
            'controle_combustivel.dashboard_combustivel_template',
            values
        )


class DashboardClientAction(http.Controller):
    """
    Controller para a Client Action do Dashboard.
    """
    
    @http.route('/combustivel/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kw):
        """
        Retorna dados do dashboard em formato JSON para client action.
        """
        # Verificar permissão
        if not request.env.user.has_group('controle_combustivel.group_analista'):
            return {'error': 'Acesso negado'}
        
        # Buscar tanque
        Tanque = request.env['controle.combustivel.tanque']
        tanque = Tanque.search([], limit=1)
        
        # Calcular período do mês atual
        hoje = fields.Date.today()
        primeiro_dia_mes = hoje.replace(day=1)
        ultimo_dia_mes = (primeiro_dia_mes + relativedelta(months=1)) - relativedelta(days=1)
        
        # Buscar abastecimentos do mês
        Abastecimento = request.env['controle.combustivel.abastecimento']
        abastecimentos_mes = Abastecimento.search([
            ('data_hora', '>=', datetime.combine(primeiro_dia_mes, datetime.min.time())),
            ('data_hora', '<=', datetime.combine(ultimo_dia_mes, datetime.max.time())),
            ('state', '=', 'confirmado'),
        ])
        
        # Calcular totais
        consumo_litros = sum(abastecimentos_mes.mapped('quantidade_litros'))
        consumo_valor = sum(abastecimentos_mes.mapped('total'))
        
        # Buscar último abastecimento
        ultimo = Abastecimento.search([
            ('state', '=', 'confirmado'),
        ], order='data_hora desc', limit=1)
        
        return {
            'tanque': {
                'name': tanque.name if tanque else '',
                'capacidade': tanque.capacidade if tanque else 0,
                'estoque_atual': tanque.estoque_atual if tanque else 0,
                'percentual_nivel': tanque.percentual_nivel if tanque else 0,
                'status_nivel': tanque.status_nivel if tanque else '',
            },
            'consumo_litros': consumo_litros,
            'consumo_valor': consumo_valor,
            'total_abastecimentos': len(abastecimentos_mes),
            'ultimo_abastecimento': {
                'name': ultimo.name if ultimo else '',
                'data_hora': ultimo.data_hora.strftime('%d/%m/%Y %H:%M') if ultimo else '',
                'equipamento': ultimo.equipamento_id.name if ultimo else '',
                'placa': ultimo.placa or '' if ultimo else '',
                'quantidade': ultimo.quantidade_litros if ultimo else 0,
                'usuario': ultimo.usuario_id.name if ultimo else '',
            } if ultimo else None,
        }
