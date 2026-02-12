# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from datetime import datetime
from dateutil.relativedelta import relativedelta

class DashboardCombustivelController(http.Controller):
    """ Controller para o Dashboard de Combustível. """

    @http.route('/combustivel/dashboard', type='http', auth='user', website=False)
    def dashboard(self, **kw):
        # Permissões
        if not request.env.user.has_group('controle_combustivel.group_analista'):
            return request.redirect('/web')
        
        # Dados do Tanque
        tanque = request.env['controle.combustivel.tanque'].search([], limit=1)
        if not tanque:
            tanque = request.env['controle.combustivel.tanque'].create({'name': 'Tanque Principal', 'capacidade': 6000.0})
        
        # Filtros
        vehicle_id = int(kw.get('vehicle_id', 0))
        driver_id = int(kw.get('driver_id', 0))
        
        # Período
        hoje = fields.Date.today()
        p_dia = hoje.replace(day=1)
        u_dia = (p_dia + relativedelta(months=1)) - relativedelta(days=1)
        
        domain = [
            ('data_hora', '>=', datetime.combine(p_dia, datetime.min.time())),
            ('data_hora', '<=', datetime.combine(u_dia, datetime.max.time())),
            ('state', '=', 'confirmado'),
        ]
        if vehicle_id: domain.append(('equipamento_id', '=', vehicle_id))
        if driver_id: domain.append(('motorista_id', '=', driver_id))
            
        abastecimentos = request.env['controle.combustivel.abastecimento'].search(domain)
        
        # Totais e KPIs
        litros = sum(a.quantidade_litros or 0.0 for a in abastecimentos)
        valor = sum(a.total or 0.0 for a in abastecimentos)
        total_km = sum(a.km_percorrido or 0.0 for a in abastecimentos)
        avg_kml = total_km / litros if litros > 0 else 0
        avg_cost_km = valor / total_km if total_km > 0 else 0
        
        # Projeção de Estoque
        d_passados = max(1, hoje.day)
        consumo_dia = litros / d_passados
        dias_restantes = int(tanque.estoque_atual / consumo_dia) if consumo_dia > 0 else 0
        
        # Alertas de Desvio (queda > 20% da média do veículo)
        veiculos_alerta = []
        if not vehicle_id:
            for v in abastecimentos.mapped('equipamento_id'):
                abasts_v = abastecimentos.filtered(lambda a: a.equipamento_id == v)
                if len(abasts_v) >= 2:
                    media_v = sum(a.consumo_kml or 0.0 for a in abasts_v) / len(abasts_v)
                    for a in abasts_v:
                        if 0 < a.consumo_kml < (media_v * 0.8):
                            veiculos_alerta.append({'veiculo': v.name, 'placa': v.license_plate, 'consumo': a.consumo_kml, 'media': media_v})
                            break
        
        # Gráfico últimos 7 dias
        consumo_7d = []
        for i in range(6, -1, -1):
            dia = hoje - relativedelta(days=i)
            l_dia = sum(request.env['controle.combustivel.abastecimento'].search([
                ('data_hora', '>=', datetime.combine(dia, datetime.min.time())),
                ('data_hora', '<=', datetime.combine(dia, datetime.max.time())),
                ('state', '=', 'confirmado'),
            ]).mapped('quantidade_litros'))
            
            # Altura proporcional para o gráfico CSS (seguro)
            divisor = max(10, (litros / max(1, len(abastecimentos))) * 3) if len(abastecimentos) > 0 else 100
            altura = min(100, (l_dia / divisor) * 100)
            consumo_7d.append({'dia': dia.strftime('%d/%m'), 'litros': l_dia, 'altura': altura})

        # Renderização
        meses = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
        return request.render('controle_combustivel.dashboard_combustivel_template', {
            'tanque': tanque, 'consumo_litros': litros, 'consumo_valor': valor,
            'total_abastecimentos': len(abastecimentos), 'periodo_mes': f"{meses[hoje.month]}/{hoje.year}",
            'ultimo_abastecimento': request.env['controle.combustivel.abastecimento'].search([('state', '=', 'confirmado')], order='data_hora desc', limit=1),
            'data_atualizacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'consumo_diario': consumo_7d, 'avg_kml': avg_kml, 'avg_cost_km': avg_cost_km, 'dias_restantes': dias_restantes,
            'veiculos_alerta': veiculos_alerta[:3], 'vehicles': request.env['fleet.vehicle'].search([]),
            'drivers': request.env['res.partner'].search([('is_company', '=', False)]),
            'selected_vehicle': vehicle_id, 'selected_driver': driver_id,
            'action_abastecimento': request.env.ref('controle_combustivel.action_abastecimento_tree').id,
            'cor_badge': 'bg-success' if tanque.percentual_nivel > 30 else ('bg-warning' if tanque.percentual_nivel >= 15 else 'bg-danger'),
            'cor_progress': 'bg-success' if tanque.percentual_nivel > 30 else ('bg-warning' if tanque.percentual_nivel >= 15 else 'bg-danger'),
            'cor_tank': 'tank-green' if tanque.percentual_nivel > 30 else ('tank-yellow' if tanque.percentual_nivel >= 15 else 'tank-red'),
        })
