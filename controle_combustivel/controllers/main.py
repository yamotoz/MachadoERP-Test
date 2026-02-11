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
        
        # Filtros dinâmicos (kw)
        vehicle_id = int(kw.get('vehicle_id', 0))
        driver_id = int(kw.get('driver_id', 0))
        
        # Calcular período do mês atual
        hoje = fields.Date.today()
        primeiro_dia_mes = hoje.replace(day=1)
        ultimo_dia_mes = (primeiro_dia_mes + relativedelta(months=1)) - relativedelta(days=1)
        
        # Base de busca
        Abastecimento = request.env['controle.combustivel.abastecimento']
        domain = [
            ('data_hora', '>=', datetime.combine(primeiro_dia_mes, datetime.min.time())),
            ('data_hora', '<=', datetime.combine(ultimo_dia_mes, datetime.max.time())),
            ('state', '=', 'confirmado'),
        ]
        
        if vehicle_id:
            domain.append(('equipamento_id', '=', vehicle_id))
        if driver_id:
            domain.append(('motorista_id', '=', driver_id))
            
        abastecimentos_mes = Abastecimento.search(domain)
        
        # Calcular totais (Defensivo contra Nones)
        consumo_litros = sum(a.quantidade_litros or 0.0 for a in abastecimentos_mes)
        consumo_valor = sum(a.total or 0.0 for a in abastecimentos_mes)
        total_abastecimentos = len(abastecimentos_mes)

        # KPIs de Eficiência da Frota
        total_km = sum(a.km_percorrido or 0.0 for a in abastecimentos_mes)
        avg_kml = total_km / consumo_litros if consumo_litros > 0 else 0
        avg_cost_km = consumo_valor / total_km if total_km > 0 else 0
        
        # Estimativa de Duração do Estoque (Média de consumo diário)
        dias_passados = max(1, hoje.day)
        consumo_diario_medio = consumo_litros / dias_passados
        dias_restantes = int(tanque.estoque_atual / consumo_diario_medio) if consumo_diario_medio > 0 else 0
        
        veiculos_alerta = []
        if not vehicle_id:
            for v in abastecimentos_mes.mapped('equipamento_id'):
                abasts_v = abastecimentos_mes.filtered(lambda a: a.equipamento_id == v)
                if len(abasts_v) >= 2:
                    media_v = sum(a.consumo_kml or 0.0 for a in abasts_v) / len(abasts_v)
                    for a in abasts_v:
                        if a.consumo_kml and a.consumo_kml > 0 and a.consumo_kml < (media_v * 0.8):
                            veiculos_alerta.append({
                                'veiculo': v.name,
                                'placa': v.license_plate,
                                'consumo': a.consumo_kml or 0.0,
                                'media': media_v
                            })
                            break
        
        # Buscar último abastecimento
        ultimo_abastecimento = Abastecimento.search([
            ('state', '=', 'confirmado'),
        ], order='data_hora desc', limit=1)
        
        # Definir cores baseado no nível (Novo: Amarelo 30%, Vermelho 15%)
        percentual = tanque.percentual_nivel if tanque else 0
        if percentual > 30:
            cor_badge = 'bg-success'
            cor_progress = 'bg-success'
            cor_tank = 'tank-green'
        elif percentual >= 15:
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
            
            # Cálculo de altura de barra seguro contra divisão por zero
            media_litros_mes = consumo_litros / max(1, total_abastecimentos)
            divisor = max(10, media_litros_mes * 3)
            altura = min(100, (litros_dia / divisor) * 100) if total_abastecimentos > 0 else 0
            
            consumo_diario.append({
                'dia': dia.strftime('%d/%m'),
                'litros': litros_dia,
                'altura': altura
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
            'avg_kml': avg_kml,
            'avg_cost_km': avg_cost_km,
            'dias_restantes': dias_restantes,
            'veiculos_alerta': veiculos_alerta[:3], # Top 3 alertas
            'vehicles': request.env['fleet.vehicle'].search([]),
            'drivers': request.env['res.partner'].search([('is_company', '=', False)]),
            'selected_vehicle': vehicle_id,
            'selected_driver': driver_id,
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
