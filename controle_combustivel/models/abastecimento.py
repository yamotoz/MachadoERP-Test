# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Abastecimento(models.Model):
    """ Registro de abastecimentos vinculado à frota. """
    _name = 'controle.combustivel.abastecimento'
    _description = 'Abastecimento de Combustível'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'data_hora desc, id desc'
    _rec_name = 'name'

    # Identificação
    name = fields.Char(string='Número', required=True, copy=False, readonly=True, default=lambda self: _('Novo'))
    
    # Dados Gerais
    data_hora = fields.Datetime(string='Data/Hora', required=True, default=fields.Datetime.now, tracking=True)
    equipamento_id = fields.Many2one('fleet.vehicle', string='Veículo/Equipamento', required=True, tracking=True)
    placa = fields.Char(related='equipamento_id.license_plate', string='Placa', store=True, readonly=True)
    motorista_id = fields.Many2one('res.partner', string='Motorista', tracking=True, domain="[('is_company', '=', False)]")
    usuario_id = fields.Many2one('res.users', string='Registrado por', default=lambda self: self.env.user, readonly=True, tracking=True)
    tanque_id = fields.Many2one('controle.combustivel.tanque', string='Tanque', required=True, default=lambda self: self._default_tanque(), tracking=True)
    
    # Medição e Consumo
    horimetro_odometro = fields.Float(string='Horímetro/Odômetro', required=True, tracking=True)
    tipo_medicao = fields.Selection([('horimetro', 'Horímetro (h)'), ('odometro', 'Odômetro (km)')], string='Tipo de Medição', default='odometro')
    quantidade_litros = fields.Float(string='Quantidade (L)', required=True, tracking=True)
    valor_por_litro = fields.Float(string='Valor por Litro (R$)', required=True, tracking=True, digits=(12, 4))
    total = fields.Float(string='Total (R$)', compute='_compute_total', store=True, readonly=True, digits=(12, 2))
    
    # Eficiência
    leitura_anterior = fields.Float(string='Leitura Anterior', compute='_compute_eficiencia', store=True)
    km_percorrido = fields.Float(string='KM/H Percorrido', compute='_compute_eficiencia', store=True)
    consumo_kml = fields.Float(string='Consumo (km/L)', compute='_compute_eficiencia', store=True, digits=(12, 2))
    custo_km = fields.Float(string='Custo por KM (R$)', compute='_compute_eficiencia', store=True, digits=(12, 2))
    
    # Estado e Diversos
    state = fields.Selection([('rascunho', 'Rascunho'), ('confirmado', 'Confirmado'), ('cancelado', 'Cancelado')], string='Status', default='rascunho', tracking=True, copy=False)
    observacao = fields.Text(string='Observações')
    comprovante = fields.Binary(string='Comprovante', attachment=True)
    comprovante_filename = fields.Char(string='Nome do Arquivo')
    estoque_disponivel = fields.Float(related='tanque_id.estoque_atual', string='Estoque Disponível', readonly=True)
    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.company)

    def _default_tanque(self):
        return self.env['controle.combustivel.tanque'].search([], limit=1)

    @api.depends('quantidade_litros', 'valor_por_litro')
    def _compute_total(self):
        for record in self:
            record.total = record.quantidade_litros * record.valor_por_litro

    @api.depends('equipamento_id', 'horimetro_odometro', 'state', 'quantidade_litros', 'total')
    def _compute_eficiencia(self):
        for record in self:
            if record.state != 'confirmado':
                record.leitura_anterior = record.km_percorrido = record.consumo_kml = record.custo_km = 0
                continue

            ultimo = self.search([
                ('equipamento_id', '=', record.equipamento_id.id),
                ('state', '=', 'confirmado'),
                ('id', '<', record.id),
                ('tipo_medicao', '=', record.tipo_medicao),
            ], order='data_hora desc, id desc', limit=1)

            if ultimo:
                record.leitura_anterior = ultimo.horimetro_odometro
                record.km_percorrido = record.horimetro_odometro - ultimo.horimetro_odometro
                record.consumo_kml = record.km_percorrido / record.quantidade_litros if record.quantidade_litros > 0 else 0
                record.custo_km = record.total / record.km_percorrido if record.km_percorrido > 0 else 0
            else:
                record.leitura_anterior = record.km_percorrido = record.consumo_kml = record.custo_km = 0

    @api.onchange('quantidade_litros', 'valor_por_litro')
    def _onchange_calcular_total(self):
        self.total = self.quantidade_litros * self.valor_por_litro
    
    @api.onchange('quantidade_litros')
    def _onchange_verificar_estoque(self):
        if self.tanque_id and self.quantidade_litros > self.tanque_id.estoque_atual:
            return {'warning': {'title': _('Estoque Baixo'), 'message': _('Quantidade excede o disponível.')}}

    @api.onchange('equipamento_id')
    def _onchange_equipamento(self):
        if self.equipamento_id.driver_id:
            self.motorista_id = self.equipamento_id.driver_id

    @api.constrains('quantidade_litros', 'valor_por_litro', 'horimetro_odometro')
    def _check_valores_positivos(self):
        for record in self:
            if record.quantidade_litros <= 0 or record.valor_por_litro <= 0:
                raise ValidationError(_('Valores de quantidade e preço devem ser maiores que zero.'))
            if record.horimetro_odometro < 0:
                raise ValidationError(_('Medição não pode ser negativa.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Novo')) == _('Novo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('controle.combustivel.abastecimento') or _('Novo')
        return super().create(vals_list)

    def write(self, vals):
        for record in self:
            if record.state in ['confirmado', 'cancelado'] and not self.env.user.has_group('controle_combustivel.group_administrador'):
                raise UserError(_('Registros confirmados não podem ser editados.'))
        return super(Abastecimento, self).write(vals)

    def unlink(self):
        for record in self:
            if record.state == 'confirmado':
                raise UserError(_('Não é possível excluir abastecimentos confirmados.'))
        return super(Abastecimento, self).unlink()

    def action_confirmar(self):
        for record in self:
            if record.state != 'rascunho': continue
            if not record.tanque_id.verificar_disponibilidade(record.quantidade_litros):
                raise ValidationError(_('Estoque insuficiente!'))
            record.tanque_id.consumir_combustivel(record.quantidade_litros)
            record.state = 'confirmado'
            record.message_post(body=_('Confirmado: %.2f L') % record.quantidade_litros)
        return True

    def action_cancelar(self):
        for record in self:
            if record.state == 'confirmado' and not self.env.user.has_group('controle_combustivel.group_administrador'):
                raise UserError(_('Somente administradores cancelam registros confirmados.'))
            record.state = 'cancelado'
        return True

    def action_voltar_rascunho(self):
        self.filtered(lambda r: r.state == 'cancelado').write({'state': 'rascunho'})
        return True

    def action_imprimir(self):
        return self.env.ref('controle_combustivel.action_report_abastecimento').report_action(self)
