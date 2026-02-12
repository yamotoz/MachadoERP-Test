# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class TanqueCombustivel(models.Model):
    """ Gerenciamento do tanque de combustível (6.000 L). """
    _name = 'controle.combustivel.tanque'
    _description = 'Tanque de Combustível'
    _rec_name = 'name'

    name = fields.Char(string='Nome', required=True, default='Tanque Principal')
    capacidade = fields.Float(string='Capacidade (L)', default=6000.0, readonly=True)
    estoque_atual = fields.Float(string='Estoque Atual (L)', compute='_compute_estoque_atual', store=True)
    estoque_manual = fields.Float(string='Estoque Inicial', default=0.0)
    percentual_nivel = fields.Float(string='Nível (%)', compute='_compute_percentual_nivel', store=True)
    cor_indicador = fields.Char(string='Cor', compute='_compute_cor_indicador')
    status_nivel = fields.Selection([('critico', 'Crítico'), ('atencao', 'Atenção'), ('normal', 'Normal')], string='Status', compute='_compute_cor_indicador')
    
    total_entradas = fields.Float(string='Total Entradas (L)', compute='_compute_movimentacoes', store=True)
    total_saidas = fields.Float(string='Total Saídas (L)', compute='_compute_movimentacoes', store=True)
    
    abastecimento_ids = fields.One2many('controle.combustivel.abastecimento', 'tanque_id', string='Abastecimentos')
    entrada_ids = fields.One2many('controle.combustivel.entrada', 'tanque_id', string='Entradas')
    active = fields.Boolean(default=True)

    @api.depends('estoque_manual', 'total_entradas', 'total_saidas')
    def _compute_estoque_atual(self):
        for record in self:
            record.estoque_atual = (record.estoque_manual or 0.0) + (record.total_entradas or 0.0) - (record.total_saidas or 0.0)

    @api.depends('estoque_atual', 'capacidade')
    def _compute_percentual_nivel(self):
        for record in self:
            record.percentual_nivel = (record.estoque_atual / record.capacidade) * 100 if record.capacidade > 0 else 0

    @api.depends('percentual_nivel')
    def _compute_cor_indicador(self):
        for record in self:
            p = record.percentual_nivel
            if p > 50: record.cor_indicador, record.status_nivel = '#28A745', 'normal'
            elif p >= 20: record.cor_indicador, record.status_nivel = '#FFC107', 'atencao'
            else: record.cor_indicador, record.status_nivel = '#A43A2F', 'critico'

    @api.depends('abastecimento_ids.state', 'abastecimento_ids.quantidade_litros', 'entrada_ids.state', 'entrada_ids.quantidade_litros')
    def _compute_movimentacoes(self):
        for record in self:
            record.total_saidas = sum(record.abastecimento_ids.filtered(lambda a: a.state == 'confirmado').mapped('quantidade_litros'))
            record.total_entradas = sum(record.entrada_ids.filtered(lambda e: e.state == 'confirmado').mapped('quantidade_litros'))

    def consuming_combustivel(self, quantidade):
        if quantidade > self.estoque_atual:
            raise ValidationError(_('Estoque insuficiente!'))
        return True

    def adicionar_combustivel(self, quantidade):
        if self.estoque_atual + quantidade > self.capacidade:
            raise ValidationError(_('Excede a capacidade do tanque!'))
        return True

    def verificar_disponibilidade(self, quantidade):
        return self.estoque_atual >= quantidade

    def consumir_combustivel(self, quantidade):
        """ Apenas validação, o cálculo é feito via compute dependendo do estado do abastecimento. """
        if quantidade > self.estoque_atual:
            raise ValidationError(_('Estoque insuficiente!'))
        return True

class EntradaCombustivel(models.Model):
    """ Registro de reposição de combustível no tanque. """
    _name = 'controle.combustivel.entrada'
    _description = 'Entrada de Combustível'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'data_hora desc'

    name = fields.Char(string='Referência', required=True, copy=False, readonly=True, default=lambda self: _('Novo'))
    tanque_id = fields.Many2one('controle.combustivel.tanque', string='Tanque', required=True, default=lambda self: self._default_tanque())
    data_hora = fields.Datetime(string='Data/Hora', required=True, default=fields.Datetime.now, tracking=True)
    quantidade_litros = fields.Float(string='Quantidade (L)', required=True, tracking=True)
    valor_por_litro = fields.Float(string='Valor por Litro (R$)', tracking=True)
    total = fields.Float(string='Total (R$)', compute='_compute_total', store=True)
    fornecedor = fields.Char(string='Fornecedor')
    nota_fiscal = fields.Char(string='Nota Fiscal')
    state = fields.Selection([('rascunho', 'Rascunho'), ('confirmado', 'Confirmado'), ('cancelado', 'Cancelado')], string='Status', default='rascunho', tracking=True)
    usuario_id = fields.Many2one('res.users', string='Responsável', default=lambda self: self.env.user, readonly=True)

    def _default_tanque(self):
        return self.env['controle.combustivel.tanque'].search([], limit=1)

    @api.depends('quantidade_litros', 'valor_por_litro')
    def _compute_total(self):
        for record in self:
            record.total = record.quantidade_litros * record.valor_por_litro

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Novo')) == _('Novo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('controle.combustivel.entrada') or _('Novo')
        return super().create(vals_list)

    def action_confirmar(self):
        for record in self:
            if record.state != 'rascunho': continue
            record.tanque_id.adicionar_combustivel(record.quantidade_litros)
            record.state = 'confirmado'
        return True

    def action_cancelar(self):
        for record in self:
            if record.state == 'confirmado':
                raise ValidationError(_('Não é possível cancelar entrada confirmada.'))
            record.state = 'cancelado'
        return True

    def write(self, vals):
        for record in self:
            if record.state in ['confirmado', 'cancelado'] and not self.env.user.has_group('controle_combustivel.group_administrador'):
                raise UserError(_('Registros confirmados não podem ser editados.'))
        return super(EntradaCombustivel, self).write(vals)

    def unlink(self):
        for record in self:
            if record.state == 'confirmado':
                raise UserError(_('Não é possível excluir entradas confirmadas.'))
        return super(EntradaCombustivel, self).unlink()
