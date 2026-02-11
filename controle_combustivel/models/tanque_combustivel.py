# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TanqueCombustivel(models.Model):
    """
    Modelo singleton para gerenciar o tanque de combustível.
    Capacidade fixa de 6.000 litros.
    """
    _name = 'controle.combustivel.tanque'
    _description = 'Tanque de Combustível'
    _rec_name = 'name'

    name = fields.Char(
        string='Nome',
        required=True,
        default='Tanque Principal',
    )
    capacidade = fields.Float(
        string='Capacidade (L)',
        default=6000.0,
        readonly=True,
        help='Capacidade máxima do tanque em litros',
    )
    estoque_atual = fields.Float(
        string='Estoque Atual (L)',
        compute='_compute_estoque_atual',
        store=True,
        help='Quantidade atual de combustível no tanque',
    )
    estoque_manual = fields.Float(
        string='Estoque Inicial',
        default=0.0,
        help='Estoque inicial ou ajuste manual',
    )
    percentual_nivel = fields.Float(
        string='Nível (%)',
        compute='_compute_percentual_nivel',
        store=True,
        help='Percentual de preenchimento do tanque',
    )
    cor_indicador = fields.Char(
        string='Cor do Indicador',
        compute='_compute_cor_indicador',
        help='Cor para exibição visual do nível',
    )
    status_nivel = fields.Selection([
        ('critico', 'Crítico'),
        ('atencao', 'Atenção'),
        ('normal', 'Normal'),
    ], string='Status do Nível', compute='_compute_cor_indicador')
    ultima_entrada = fields.Datetime(
        string='Última Entrada',
        help='Data/hora da última reposição de combustível',
    )
    ultima_saida = fields.Datetime(
        string='Última Saída',
        help='Data/hora do último abastecimento realizado',
    )
    total_entradas = fields.Float(
        string='Total Entradas (L)',
        compute='_compute_movimentacoes',
        store=True,
        help='Total de litros recebidos',
    )
    total_saidas = fields.Float(
        string='Total Saídas (L)',
        compute='_compute_movimentacoes',
        store=True,
        help='Total de litros consumidos em abastecimentos',
    )
    abastecimento_ids = fields.One2many(
        'controle.combustivel.abastecimento',
        'tanque_id',
        string='Abastecimentos',
    )
    entrada_ids = fields.One2many(
        'controle.combustivel.entrada',
        'tanque_id',
        string='Entradas',
    )
    active = fields.Boolean(default=True)

    @api.depends('estoque_manual', 'total_entradas', 'total_saidas')
    def _compute_estoque_atual(self):
        """Calcula o estoque atual baseado em entradas e saídas."""
        for record in self:
            # Garante que os valores sejam numéricos
            manual = record.estoque_manual or 0.0
            entradas = record.total_entradas or 0.0
            saidas = record.total_saidas or 0.0
            
            record.estoque_atual = manual + entradas - saidas

    @api.depends('estoque_atual', 'capacidade')
    def _compute_percentual_nivel(self):
        """Calcula o percentual de preenchimento do tanque."""
        for record in self:
            if record.capacidade > 0:
                record.percentual_nivel = (record.estoque_atual / record.capacidade) * 100
            else:
                record.percentual_nivel = 0.0

    @api.depends('percentual_nivel')
    def _compute_cor_indicador(self):
        """Define cor e status baseado no nível do tanque."""
        for record in self:
            percentual = record.percentual_nivel
            if percentual > 50:
                record.cor_indicador = '#28A745'  # Verde
                record.status_nivel = 'normal'
            elif percentual >= 20:
                record.cor_indicador = '#FFC107'  # Amarelo
                record.status_nivel = 'atencao'
            else:
                record.cor_indicador = '#A43A2F'  # Vermelho
                record.status_nivel = 'critico'

    @api.depends(
        'abastecimento_ids.state', 
        'abastecimento_ids.quantidade_litros',
        'entrada_ids.state', 
        'entrada_ids.quantidade_litros'
    )
    def _compute_movimentacoes(self):
        """Calcula totais de entrada e saída a partir dos abastecimentos vinculados."""
        for record in self:
            # Total de saídas: soma de todos os abastecimentos CONFIRMADOS deste tanque
            saidas = sum(record.abastecimento_ids.filtered(
                lambda a: a.state == 'confirmado'
            ).mapped('quantidade_litros'))
            record.total_saidas = saidas
            
            # Total de entradas: soma de todas as entradas CONFIRMADAS deste tanque
            entradas = sum(record.entrada_ids.filtered(
                lambda e: e.state == 'confirmado'
            ).mapped('quantidade_litros'))
            record.total_entradas = entradas

    def action_recalculate_stock(self):
        """Método manual para forçar o recálculo se necessário."""
        self._compute_movimentacoes()
        self._compute_estoque_atual()
        return True

    def adicionar_combustivel(self, quantidade):
        """
        Adiciona combustível ao tanque.
        Chamado ao receber compras ou fazer ajustes positivos.
        
        :param quantidade: Litros a adicionar
        :raises ValidationError: Se quantidade for inválida ou exceder capacidade
        """
        self.ensure_one()
        if quantidade <= 0:
            raise ValidationError(_('A quantidade deve ser maior que zero.'))
        
        novo_estoque = self.estoque_atual + quantidade
        if novo_estoque > self.capacidade:
            raise ValidationError(
                _('Quantidade excede a capacidade do tanque!\n'
                  'Capacidade: %.2f L\n'
                  'Estoque atual: %.2f L\n'
                  'Máximo que pode receber: %.2f L') % (
                    self.capacidade,
                    self.estoque_atual,
                    self.capacidade - self.estoque_atual
                )
            )
        
        self.ultima_entrada = fields.Datetime.now()
        return True

    def consumir_combustivel(self, quantidade):
        """
        Consome combustível do tanque (abastecimento).
        Valida se há estoque suficiente antes de consumir.
        
        :param quantidade: Litros a consumir
        :raises ValidationError: Se estoque insuficiente
        """
        self.ensure_one()
        if quantidade <= 0:
            raise ValidationError(_('A quantidade deve ser maior que zero.'))
        
        if quantidade > self.estoque_atual:
            raise ValidationError(
                _('❌ Estoque insuficiente!\n'
                  'Disponível: %.2f litros\n'
                  'Solicitado: %.2f litros') % (
                    self.estoque_atual,
                    quantidade
                )
            )
        
        self.ultima_saida = fields.Datetime.now()
        return True

    def verificar_disponibilidade(self, quantidade):
        """
        Verifica se há quantidade disponível sem consumir.
        
        :param quantidade: Litros a verificar
        :return: True se disponível, False caso contrário
        """
        self.ensure_one()
        return self.estoque_atual >= quantidade


class EntradaCombustivel(models.Model):
    """
    Modelo para registrar entradas de combustível no tanque.
    Usado para controle de compras e reposições.
    """
    _name = 'controle.combustivel.entrada'
    _description = 'Entrada de Combustível'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'data_hora desc'

    name = fields.Char(
        string='Referência',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Novo'),
    )
    tanque_id = fields.Many2one(
        'controle.combustivel.tanque',
        string='Tanque',
        required=True,
        default=lambda self: self._default_tanque(),
    )
    data_hora = fields.Datetime(
        string='Data/Hora',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )
    quantidade_litros = fields.Float(
        string='Quantidade (L)',
        required=True,
        tracking=True,
    )
    valor_por_litro = fields.Float(
        string='Valor por Litro (R$)',
        tracking=True,
    )
    total = fields.Float(
        string='Total (R$)',
        compute='_compute_total',
        store=True,
    )
    fornecedor = fields.Char(
        string='Fornecedor',
    )
    nota_fiscal = fields.Char(
        string='Nota Fiscal',
    )
    observacao = fields.Text(
        string='Observações',
    )
    state = fields.Selection([
        ('rascunho', 'Rascunho'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ], string='Status', default='rascunho', tracking=True)
    usuario_id = fields.Many2one(
        'res.users',
        string='Responsável',
        default=lambda self: self.env.user,
        readonly=True,
    )

    def _default_tanque(self):
        """Retorna o tanque padrão."""
        return self.env['controle.combustivel.tanque'].search([], limit=1)

    @api.depends('quantidade_litros', 'valor_por_litro')
    def _compute_total(self):
        """Calcula o valor total da entrada."""
        for record in self:
            record.total = record.quantidade_litros * record.valor_por_litro

    @api.model_create_multi
    def create(self, vals_list):
        """Gera sequência automática na criação."""
        for vals in vals_list:
            if vals.get('name', _('Novo')) == _('Novo'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'controle.combustivel.entrada'
                ) or _('Novo')
        return super().create(vals_list)

    def action_confirmar(self):
        """Confirma a entrada de combustível."""
        for record in self:
            if record.state != 'rascunho':
                continue
            
            # Valida e adiciona ao tanque
            record.tanque_id.adicionar_combustivel(record.quantidade_litros)
            record.state = 'confirmado'
        return True

    def action_cancelar(self):
        """Cancela a entrada de combustível."""
        for record in self:
            if record.state == 'confirmado':
                raise ValidationError(
                    _('Não é possível cancelar uma entrada já confirmada.')
                )
            record.state = 'cancelado'
        return True

    def action_voltar_rascunho(self):
        """Retorna ao status de rascunho."""
        for record in self:
            if record.state == 'cancelado':
                record.state = 'rascunho'
        return True
