# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class Abastecimento(models.Model):
    """
    Modelo principal para registro de abastecimentos de combustível.
    Integrado com módulo de Frota do Odoo.
    """
    _name = 'controle.combustivel.abastecimento'
    _description = 'Abastecimento de Combustível'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'data_hora desc, id desc'
    _rec_name = 'name'

    # === Campos de Identificação ===
    name = fields.Char(
        string='Número',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Novo'),
        help='Número de identificação do abastecimento',
    )
    
    # === Campos de Data/Hora ===
    data_hora = fields.Datetime(
        string='Data/Hora',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help='Data e hora do abastecimento',
    )
    
    # === Relações ===
    equipamento_id = fields.Many2one(
        'fleet.vehicle',
        string='Veículo/Equipamento',
        required=True,
        tracking=True,
        help='Veículo ou equipamento abastecido',
    )
    placa = fields.Char(
        related='equipamento_id.license_plate',
        string='Placa',
        store=True,
        readonly=True,
    )
    motorista_id = fields.Many2one(
        'res.partner',
        string='Motorista',
        tracking=True,
        domain="[('is_company', '=', False)]",
        help='Motorista responsável pelo veículo',
    )
    usuario_id = fields.Many2one(
        'res.users',
        string='Registrado por',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True,
        help='Usuário que registrou o abastecimento',
    )
    tanque_id = fields.Many2one(
        'controle.combustivel.tanque',
        string='Tanque',
        required=True,
        default=lambda self: self._default_tanque(),
        tracking=True,
        help='Tanque de origem do combustível',
    )
    
    # === Campos de Medição ===
    horimetro_odometro = fields.Float(
        string='Horímetro/Odômetro',
        required=True,
        tracking=True,
        help='Leitura atual do horímetro (horas) ou odômetro (km)',
    )
    tipo_medicao = fields.Selection([
        ('horimetro', 'Horímetro (h)'),
        ('odometro', 'Odômetro (km)'),
    ], string='Tipo de Medição', default='odometro')
    
    # === Campos Financeiros ===
    quantidade_litros = fields.Float(
        string='Quantidade (L)',
        required=True,
        tracking=True,
        help='Quantidade de litros abastecidos',
    )
    valor_por_litro = fields.Float(
        string='Valor por Litro (R$)',
        required=True,
        tracking=True,
        digits=(12, 4),
        help='Preço por litro do combustível',
    )
    total = fields.Float(
        string='Total (R$)',
        compute='_compute_total',
        store=True,
        readonly=True,
        digits=(12, 2),
        help='Valor total do abastecimento',
    )
    
    # === Campos de Estado ===
    state = fields.Selection([
        ('rascunho', 'Rascunho'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ], string='Status', default='rascunho', tracking=True, copy=False)
    
    # === Campos Auxiliares ===
    observacao = fields.Text(
        string='Observações',
        help='Observações ou anotações sobre o abastecimento',
    )
    comprovante = fields.Binary(
        string='Comprovante',
        attachment=True,
        help='Foto ou scan do comprovante de abastecimento',
    )
    comprovante_filename = fields.Char(
        string='Nome do Arquivo',
    )
    
    # === Campos Computados de Contexto ===
    estoque_disponivel = fields.Float(
        related='tanque_id.estoque_atual',
        string='Estoque Disponível',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        default=lambda self: self.env.company,
    )

    # === Métodos de Default ===
    def _default_tanque(self):
        """Retorna o tanque padrão do sistema."""
        return self.env['controle.combustivel.tanque'].search([], limit=1)

    # === Campos Computados ===
    @api.depends('quantidade_litros', 'valor_por_litro')
    def _compute_total(self):
        """Calcula o valor total do abastecimento."""
        for record in self:
            record.total = record.quantidade_litros * record.valor_por_litro

    # === Onchange para UI ===
    @api.onchange('quantidade_litros', 'valor_por_litro')
    def _onchange_calcular_total(self):
        """Atualiza o total em tempo real na interface."""
        self.total = self.quantidade_litros * self.valor_por_litro
    
    @api.onchange('quantidade_litros')
    def _onchange_verificar_estoque(self):
        """Alerta se quantidade solicitada excede estoque."""
        if self.tanque_id and self.quantidade_litros:
            if self.quantidade_litros > self.tanque_id.estoque_atual:
                return {
                    'warning': {
                        'title': _('⚠️ Atenção: Estoque Baixo'),
                        'message': _(
                            'A quantidade solicitada (%.2f L) excede o estoque '
                            'disponível (%.2f L).\n\n'
                            'O abastecimento não poderá ser confirmado.'
                        ) % (self.quantidade_litros, self.tanque_id.estoque_atual)
                    }
                }

    @api.onchange('equipamento_id')
    def _onchange_equipamento(self):
        """Preenche motorista padrão do veículo se disponível."""
        if self.equipamento_id and self.equipamento_id.driver_id:
            self.motorista_id = self.equipamento_id.driver_id

    # === Constraints ===
    @api.constrains('quantidade_litros')
    def _check_quantidade(self):
        """Valida que a quantidade é positiva."""
        for record in self:
            if record.quantidade_litros <= 0:
                raise ValidationError(
                    _('❌ A quantidade de litros deve ser maior que zero.')
                )

    @api.constrains('valor_por_litro')
    def _check_valor(self):
        """Valida que o valor por litro é positivo."""
        for record in self:
            if record.valor_por_litro <= 0:
                raise ValidationError(
                    _('❌ O valor por litro deve ser maior que zero.')
                )

    @api.constrains('horimetro_odometro')
    def _check_medicao(self):
        """Valida que a medição é positiva."""
        for record in self:
            if record.horimetro_odometro < 0:
                raise ValidationError(
                    _('❌ O horímetro/odômetro não pode ser negativo.')
                )

    # === Métodos CRUD ===
    @api.model_create_multi
    def create(self, vals_list):
        """Gera sequência automática na criação."""
        for vals in vals_list:
            if vals.get('name', _('Novo')) == _('Novo'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'controle.combustivel.abastecimento'
                ) or _('Novo')
        return super().create(vals_list)

    def unlink(self):
        """Impede exclusão de registros confirmados."""
        for record in self:
            if record.state == 'confirmado':
                raise UserError(
                    _('Não é possível excluir abastecimentos confirmados.\n'
                      'Cancele o registro primeiro se necessário.')
                )
        return super().unlink()

    # === Ações de Workflow ===
    def action_confirmar(self):
        """
        Confirma o abastecimento.
        Valida estoque e atualiza o tanque.
        """
        for record in self:
            if record.state != 'rascunho':
                continue
            
            # Validação de tanque configurado
            if not record.tanque_id:
                raise ValidationError(
                    _('⚠️ Nenhum tanque de combustível configurado.\n'
                      'Contate o administrador do sistema.')
                )
            
            # Validação de estoque
            if not record.tanque_id.verificar_disponibilidade(record.quantidade_litros):
                raise ValidationError(
                    _('❌ Estoque insuficiente!\n\n'
                      'Disponível: %.2f litros\n'
                      'Solicitado: %.2f litros\n\n'
                      'Aguarde a reposição do tanque.') % (
                        record.tanque_id.estoque_atual,
                        record.quantidade_litros
                    )
                )
            
            # Consumir do tanque
            record.tanque_id.consumir_combustivel(record.quantidade_litros)
            
            # Atualizar estado
            record.state = 'confirmado'
            
            # Log de mensagem
            record.message_post(
                body=_('Abastecimento confirmado: %.2f litros') % record.quantidade_litros,
                message_type='notification',
            )
        
        return True

    def action_cancelar(self):
        """
        Cancela o abastecimento.
        Apenas administradores podem cancelar registros confirmados.
        """
        for record in self:
            if record.state == 'confirmado':
                # Verificar permissão de admin
                if not self.env.user.has_group('controle_combustivel.group_administrador'):
                    raise UserError(
                        _('Apenas administradores podem cancelar '
                          'abastecimentos confirmados.')
                    )
                # Nota: O estoque já foi consumido, não revertemos automaticamente
                # para evitar inconsistências. O admin deve fazer ajuste manual.
                record.message_post(
                    body=_('⚠️ Abastecimento cancelado após confirmação. '
                           'Considere ajustar o estoque manualmente se necessário.'),
                    message_type='notification',
                )
            
            record.state = 'cancelado'
        
        return True

    def action_voltar_rascunho(self):
        """Retorna ao status de rascunho (apenas de cancelado)."""
        for record in self:
            if record.state == 'cancelado':
                record.state = 'rascunho'
        return True

    # === Métodos de Relatório ===
    def action_imprimir(self):
        """Gera relatório PDF do abastecimento."""
        return self.env.ref(
            'controle_combustivel.action_report_abastecimento'
        ).report_action(self)
