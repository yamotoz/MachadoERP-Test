# PRD - Produto Requirements Document
## Sistema MachadoERP - Controle de Combustível

---

## 📋 Visão Geral

O **MachadoERP - Controle de Combustível** é um módulo desenvolvido para o Odoo Community 19.0 que oferece gerenciamento completo de abastecimento de combustível, com foco em controle de estoque, análise de eficiência e business intelligence para gestão de frotas.

### 🎯 Objetivo Principal

Transformar o controle de combustível em uma ferramenta estratégica de gestão, automatizando processos operacionais e fornecendo insights para tomada de decisão através de indicadores de eficiência e custos operacionais.

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico

- **Framework**: Odoo Community 19.0
- **Linguagem**: Python 3.13
- **Banco de Dados**: PostgreSQL
- **Frontend**: QWeb Templates + CSS/JavaScript nativo
- **Arquitetura**: MVC (Model-View-Controller)

### Estrutura do Módulo

```
controle_combustivel/
├── __init__.py                    # Inicialização do módulo
├── __manifest__.py                # Metadados e dependências
├── models/                        # Camada de dados (ORM)
│   ├── __init__.py
│   ├── abastecimento.py          # Modelo de abastecimentos
│   └── tanque_combustivel.py     # Modelo de tanque e entradas
├── views/                         # Camada de apresentação
│   ├── abastecimento_views.xml   # Views de abastecimento
│   ├── tanque_views.xml          # Views de tanque
│   ├── dashboard_views.xml       # Dashboard customizado
│   └── menu_views.xml            # Estrutura de menus
├── controllers/                   # Camada de controle HTTP
│   └── main.py                   # Controllers do dashboard
├── security/                      # Controle de acesso
│   ├── security.xml              # Grupos e privilégios
│   └── ir.model.access.csv       # ACL das models
├── data/                          # Dados iniciais
│   ├── sequence_data.xml         # Sequências numéricas
│   └── tanque_data.xml           # Tanque padrão
├── reports/                       # Relatórios
│   └── report_abastecimento.xml  # Template PDF
├── static/                        # Assets web
│   └── description/              # Icones e metadados
└── README.md                      # Documentação do módulo
```

---

## 🏢 Modelos de Dados (ORM)

### 1. Modelo Principal: Abastecimento

**Classe**: `controle.combustivel.abastecimento`

#### Campos Principais
- **Identificação**: `name` (sequencial automático), `data_hora`, `state`
- **Relacionamentos**: `equipamento_id` (fleet.vehicle), `motorista_id` (res.partner), `tanque_id`
- **Medição**: `horimetro_odometro`, `tipo_medicao` (horímetro/odômetro)
- **Financeiros**: `quantidade_litros`, `valor_por_litro`, `total` (calculado)
- **Eficiência**: `leitura_anterior`, `km_percorrido`, `consumo_kml`, `custo_km` (campos computados)
- **Responsáveis**: `usuario_id` (auto), `motorista_id`
- **Documentação**: `comprovante`, `observacao`

#### Campos Computados Avançados
```python
# Eficiência do veículo baseada no histórico
consumo_kml = km_percorrido / quantidade_litros
custo_km = total / km_percorrido
```

#### Workflow de Estados
1. **Rascunho** → Em edição
2. **Confirmado** → Registrado e estoque atualizado
3. **Cancelado** → Anulado (apenas administradores)

### 2. Modelo de Estoque: Tanque

**Classe**: `controle.combustivel.tanque`

#### Características
- **Capacidade**: 6.000 litros (configurável)
- **Singleton**: Apenas um registro ativo no sistema
- **Controle Automático**: Estoque atualizado por entradas e saídas

#### Campos Monitorados
- `estoque_atual` (calculado: manual + entradas - saídas)
- `percentual_nivel` (calculado sobre capacidade)
- `cor_indicador` (baseado no nível: verde/amarelo/vermelho)
- `ultima_entrada`, `ultima_saida` (timestamps)
- `total_entradas`, `total_saidas` (agregados)

#### Status de Nível
- **🟢 Normal** (>30%): Operação normal
- **🟡 Atenção** (15-30%): Sugestão de compra
- **🔴 Crítico** (<15%): Risco de parada

### 3. Modelo de Entradas

**Classe**: `controle.combustivel.entrada`

#### Finalidade
- Registrar compras e reposições de combustível
- Controlar fornecedores e notas fiscais
- Integrar com processos de compras

---

## 🔄 Fluxos de Negócio

### 1. Fluxo de Abastecimento

```
1. Motorista acessa sistema
2. Seleciona veículo/equipamento
3. Informa quantidade e valor por litro
4. Sistema calcula total automaticamente
5. Valida estoque disponível
6. Confirma abastecimento
7. Estoque do tanque é atualizado
8. Eficiência do veículo é calculada
```

### 2. Fluxo de Reposição

```
1. Administrador registra entrada
2. Informa quantidade e fornecedor
3. Sistema valida capacidade do tanque
4. Confirma entrada
5. Estoque é incrementado
```

### 3. Cálculos de Eficiência

O sistema calcula automaticamente:
- **Consumo médio**: km/L por abastecimento
- **Custo operacional**: R$/km 
- **Desvios**: Alertas para consumo >20% abaixo da média
- **Tendências**: Análise comparativa histórica

---

## 🎛️ Dashboard Inteligente

### Localização
Menu: Combustível → Dashboard

### Indicadores Principais

#### 1. Cards KPI
- **Estoque Disponível**: Litros atuais com indicador visual
- **Eficiência da Frota**: Consumo médio em km/L
- **Custo Operacional**: R$/km médio
- **Volume Mensal**: Total de litros e abastecimentos

#### 2. Visualizações
- **Gráfico de Consumo Diário**: Últimos 7 dias com barras proporcionais
- **Status do Tanque**: Representação visual 3D do nível
- **Último Abastecimento**: Informações detalhadas
- **Alertas de Desvio**: Veículos com consumo anômalo

#### 3. Filtros Dinâmicos
- Por veículo/equipamento
- Por motorista
- Por período personalizado

### Performance
- Carregamento otimizado com consultas eficientes
- Cache inteligente para evitar recálculos desnecessários
- Design responsivo para mobile e desktop

---

## 🔐 Sistema de Segurança

### Hierarquia de Perfis

#### 1. Motorista (Nível 1)
**Permissões**:
- ✅ Registrar próprios abastecimentos
- ✅ Visualizar abastecimentos confirmados
- ❌ Acessar relatórios gerenciais
- ❌ Alterar estoque manualmente

#### 2. Analista (Nível 2)
**Permissões**:
- ✅ Herda todas as permissões de Motorista
- ✅ Visualizar todos os registros (leitura)
- ✅ Acessar dashboard e relatórios
- ✅ Exportar dados
- ❌ Criar/editar registros de outros usuários

#### 3. Administrador (Nível 3)
**Permissões**:
- ✅ Controle total do módulo
- ✅ Configurar tanque e ajustar estoque
- ✅ Cancelar abastecimentos confirmados
- ✅ Gerenciar usuários e permissões

### Controle de Acesso

#### Record Rules
- **Motorista**: Vê apenas rascunhos próprios + todos confirmados
- **Analista**: Acesso total em modo leitura
- **Administrador**: Acesso completo (CRUD)

#### Validações em Nível de Interface
- Campos readonly dinâmicos baseados no estado
- Botões condicionais por perfil
- Alertas contextuais para validações

---

## 📊 Relatórios e Análises

### 1. Relatórios Nativos

#### Abastecimentos
- **Lista Detalhada**: Todos os campos com filtros avançados
- **Calendar View**: Visão temporal por veículo
- **Kanban Board**: Gestão visual por status

#### Análises
- **Pivot Table**: Consumo por período/veículo
- **Graph View**: Tendências e comparações
- **Filtros Inteligentes**: Hoje, mês, ano, meus registros

### 2. Indicadores de Performance

#### KPIs Calculados
- **Consumo Médio da Frota**: Σkm / Σlitros
- **Custo por Quilômetro**: Σvalor / Σkm
- **Eficiência Individual**: Por veículo/motorista
- **Previsão de Estoque**: Dias restantes baseado no consumo médio

#### Alertas Automáticos
- **Estoque Baixo**: < 30% capacidade
- **Desvio de Consumo**: >20% abaixo da média
- **Anomalias**: Padrões de consumo anormais

---

## 🎨 Design e Experiência do Usuário

### Identidade Visual

#### Cores Primárias
- **Principal**: `#A43A2F` (Vermelho corporativo)
- **Background**: `#F8F9FA` (Cinza claro)
- **Texto**: `#464A4B` (Cinza escuro)
- **Secundário**: `#697274` (Cinza médio)

#### Status Colors
- **✅ Verde**: `#28A745` (Normal/Confirmado)
- **⚠️ Amarelo**: `#FFC107` (Atenção/Rascunho)
- **❌ Vermelho**: `#A43A2F` (Crítico/Alerta)

#### Tipografia
- **Títulos**: Inter Tight, Noto Sans
- **Textos**: Inter, Noto Sans

### Experiência do Usuário

#### Princípios
- **Clareza**: Informações hierarquizadas e fáceis de ler
- **Eficiência**: Fluxos otimizados para operação rápida
- **Contexto**: Ações e informações relevantes ao estado atual
- **Responsividade**: Funcionamento em desktop e mobile

#### Padrões Odoo
- Componentes nativos do framework
- Consistência com o restante do sistema
- Padronização de espaçamentos e alinhamentos
- Feedback visual claro para ações

---

## 🔄 Integrações

### Módulos Odoo

#### Fleet (Frota)
- **Veículos**: Aproveita cadastro de equipamentos
- **Motoristas**: Integração com drivers
- **Odômetro**: Sincronização automática
- **Manutenção**: Sugestões baseadas no consumo

#### Base
- **Usuários**: Sistema de autenticação nativo
- **Empresas**: Multi-company suportado
- **Contatos**: Motoristas como res.partner

#### Mail
- **Chatter**: Log automático de atividades
- **Notificações**: Alertas por email
- **Followers**: Acompanhamento de registros

### Integrações Futuras

#### Compras (Purchase)
- **Orders**: Geração automática de ordens de compra
- **Fornecedores**: Integração com vendor registry
- **Invoicing**: Conciliação com notas fiscais

#### Contabilidade (Accounting)
- **Center Costs**: Apropriação por departamento
- **Analytics**: Relatórios gerenciais financeiros
- **Budgets**: Controle de orçamentos de combustível

---

## 🚀 Requisitos Técnicos

### Infraestrutura

#### Mínimo Recomendado
- **CPU**: 2+ cores
- **RAM**: 4GB+ 
- **Storage**: 20GB+ SSD
- **Network**: 100Mbps+

#### Software
- **OS**: Ubuntu 20.04+ / Windows 10+
- **Python**: 3.13+
- **PostgreSQL**: 13+
- **Odoo**: Community 19.0

### Dependências Python

```python
# requirements.txt (automáticas via pip install -r odoo/requirements.txt)
odoo>=19.0
psycopg2-binary>=2.9
python-dateutil>=2.8
reportlab>=3.6
```

### Performance

#### Otimizações Implementadas
- **Índices**: Campos frequentemente consultados
- **Computed Fields**: Store=True para performance
- **Batch Processing**: Operações em lote
- **Cache**: Evita recálculos desnecessários

#### Escalabilidade
- Suporta 10.000+ registros de abastecimento
- Dashboard com resposta <2 segundos
- Multi-usuário concorrente
- Backup automático configurável

---

## 📋 Testes e Qualidade

### Estratégia de Testes

#### Unitários
- **Models**: Validações de campos e regras
- **Methods**: Cálculos de eficiência
- **Constraints**: Validações de negócio

#### Integração
- **Controllers**: Endpoints HTTP
- **Security**: Permissões e record rules
- **Workflows**: Estados e transições

#### Funcionais
- **Fluxos Completos**: Abastecimento fim-a-fim
- **Dashboard**: Renderização e dados
- **Relatórios**: Geração PDF e exportação

### Qualidade de Código

#### Padrões
- **PEP 8**: Formatação Python
- **Odoo Standards**: Convenções do framework
- **Type Hints**: Anotações de tipos
- **Docstrings**: Documentação de métodos

#### Segurança
- **SQL Injection**: Proteção via ORM
- **XSS**: Sanitização automática
- **CSRF**: Tokens de segurança
- **Access Control**: Validação em múltiplas camadas

---

## 📈 Métricas de Sucesso

### Indicadores de Adoção
- **Tempo de Setup**: <30 minutos para instalação completa
- **Curva de Aprendizado**: <1 hora para usuário básico
- **Disponibilidade**: 99.9% uptime
- **Performance**: Dashboard <2 segundos

### Indicadores de Negócio
- **Redução de Desperdício**: 15-25% no consumo
- **Eficiência Operacional**: 40% menos tempo administrativo
- **Visibilidade**: 100% dos consumos rastreados
- **Tomada de Decisão**: Insights em tempo real

### ROI Estimado
- **Payback**: 3-6 meses
- **Redução de Custos**: 20% operacional
- **Produtividade**: +35% equipe operacional
- **Controle**: 100% visibilidade dos custos

---

## 🗺️ Roadmap Futuro

### Versão 2.0 (Curto Prazo)
- [ ] App Mobile nativo para motoristas
- [ ] Integração com GPS de frotas
- [ ] Relatórios avançados de BI
- [ ] Notificações push e WhatsApp

### Versão 3.0 (Médio Prazo)
- [ ] Machine Learning para previsão de consumo
- [ ] Integração com sistemas de pagamento
- [ ] Multi-tanque e multi-combustível
- [ ] API REST para integrações externas

### Versão 4.0 (Longo Prazo)
- [ ] Blockchain para auditoria imutável
- [ ] IoT para sensores de tanque
- [ ] Análise preditiva de manutenção
- [ ] Marketplace de serviços

---

## 👥 Stakeholders

### Principais Envolvidos
- **Sponsor**: Machado ERP
- **Product Owner**: Equipe de Gestão
- **Development Team**: Especialistas Odoo
- **End Users**: Motoristas, Analistas, Administradores

### Feedback Contínuo
- **Sprints**: Ciclos de 2 semanas
- **Reviews**: Reuniões semanais
- **Testing**: Ambiente UAT contínuo
- **Documentation**: Atualização constante

---

## 📞 Suporte e Manutenção

### Canal de Comunicação
- **Issues**: GitHub repository
- **Documentation**: README detalhado
- **Training**: Vídeos tutoriais
- **Community**: Fórum Odoo

### Níveis de Suporte
- **L1**: Dúvidas de uso (FAQ)
- **L2**: Problemas técnicos (Documentação)
- **L3**: Bugs críticos (Desenvolvimento)
- **L4**: Emergências (Hotline 24/7)

### Manutenção Preventiva
- **Updates**: Versões regulares de segurança
- **Backups**: Diários automatizados
- **Monitoring**: Saúde do sistema 24/7
- **Performance**: Revisões trimestrais

---

## 📄 Licença e Compliance

### Licenciamento
- **Código**: LGPL-3 (Open Source)
- **Documentação**: Creative Commons
- **Branding**: Machado ERP © 2026

### Compliance
- **LGPD**: Proteção de dados brasileira
- **ISO 27001**: Segurança da informação
- **Odoo Standards**: Conformidade com framework
- **Accessibility**: WCAG 2.1 AA

---

---

## 📝 Conclusão

O **MachadoERP - Controle de Combustível** representa a evolução do controle de combustível de uma simples necessidade operacional para uma ferramenta estratégica de gestão. Com arquitetura robusta, interface intuitiva e recursos avançados de Business Intelligence, o sistema posiciona-se como uma solução completa para empresas que buscam otimizar custos, aumentar eficiência e ganhar visibilidade sobre suas operações de combustível.

A modularidade do Odoo garante evolução contínua, enquanto o design centrado no usuário garante rápida adoção e satisfação das equipes. O sistema não apenas resolve o problema atual, mas cria uma base sólida para inovações futuras em gestão de frotas e eficiência operacional.

---

**Versão do Documento**: 1.0  
**Data**: 12/02/2026  
**Autor**: Machado ERP Development Team  
**Status**: Aprovado para Implementação