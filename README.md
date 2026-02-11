# ⛽ MachadoERP - Controle de Combustível (Odoo 19.0)

![Odoo Version](https://img.shields.io/badge/Odoo-19.0%20(Master)-714B67?logo=odoo&logoColor=white)
![Status](https://img.shields.io/badge/Status-Estável-brightgreen)
![Intelligence](https://img.shields.io/badge/Business_Intelligence-Ativo-orange)
![Design](https://img.shields.io/badge/Design-Premium_&_Dark_Mode-blue)

Este repositório contém a versão final e otimizada do módulo de **Controle de Combustível** para a **MachadoERP**. Desenvolvido para o Odoo 19, o sistema vai além do simples registro, oferecendo ferramentas de **Business Intelligence (BI)** para gestão de frotas e controle de ativos.

---

## 📋 Visão Geral
O sistema foi projetado para automatizar o ciclo completo de abastecimento, desde a entrada de combustível no tanque até a análise de eficiência de cada veículo.

### 🚀 Diferenciais de Modelo Geral:
*   **Gestão de Eficiência (KPIs)**: Cálculo automático de **km/L** e **Custo por Quilômetro (R$/km)** em cada abastecimento.
*   **Dashboard Inteligente 2.0**: Interface QWeb de alto desempenho com:
    *   **Filtros Dinâmicos**: Filtre instantaneamente por Veículo, Motorista ou Período.
    *   **Gráfico de Tendência**: Visualização de consumo diário com média móvel para detecção de anomalias.
    *   **Tanque Visual 3D**: Monitoramento animado do nível do tanque com alertas visuais.
*   **Detecção de Fraudes e Desvios**: Sistema de alertas automáticos para consumos acima da média histórica do veículo (>20% desvio).
*   **Gestão Preditiva**: Estimativa inteligente de quantos dias o estoque atual irá durar com base no consumo recente.
*   **Dark Mode Nativo**: Compatibilidade total com o novo tema escuro do Odoo 19.

---

## 🛠️ Funcionalidades Detalhadas

### 1. Dashboards e Análise
- **Cards de BI**: Visualização rápida de Consumo Total, Valor Gasto, Eficiência da Frota e Abastecimentos Realizados.
- **Alertas de Manutenção**: Identificação de gargalos operacionais e necessidade de revisão mecânica baseada no consumo.
- **Filtros em Tempo Real**: Recalculo instantâneo de todas as métricas do dashboard ao selecionar um veículo/motorista.

### 2. Controle de Estoque (Tanque)
- **Capacidade Configurável**: Padronizado em 6.000L com suporte a múltiplos tanques.
- **Alertas de Nível**: 
    - 🟢 **Normal** (> 30%)
    - 🟡 **Atenção** (15% - 30%) - Sugestão de compra.
    - 🔴 **Crítico** (< 15%) - Risco de interrupção operacional.

### 3. Integração e Segurança
- **Frota (Fleet)**: Sincronização automática com odômetros e fichas de veículos.
- **Segurança Hierárquica**:
    - **Motorista**: Apenas registra abastecimentos.
    - **Analista**: Acessa dashboard, relatórios e filtros.
    - **Administrador**: Controle total, cancelamentos e gestão de estoque.

---

## 📂 Estrutura do Projeto

```text
MachadoERP-Test/
├── controle_combustivel/    # Módulo Odoo (Addon)
│   ├── models/              # Lógica de BI e Cálculos de Eficiência
│   ├── views/               # Interfaces, Dashboards e Filtros
│   ├── static/src/css/      # Styling Premium e Dark Mode Support
│   ├── reports/             # Comprovantes PDF Profissionais
│   ├── security/            # Gestão de Grupos e Privilégios
│   └── data/                # Sequências e Dados Iniciais
├── docs/                    # Documentação Técnica
│   ├── prompt1.md           # Requisitos de Negócio Originais
│   ├── A_ser_feito.md       # Histórico de Evolução
│   └── anotações.md         # Notas de Implementação
├── odoo-19.0/               # Core do Odoo 19 Engine
└── README.md                # Este Manual
```

---

## 🚀 Como Executar

1. **Inicie o Ambiente Virtual**: `.\odoo-venv\Scripts\activate`
2. **Execute o Odoo**:
   ```bash
   .\odoo-venv\Scripts\python.exe odoo-19.0\odoo-bin -r odoo -w odoo --db_host 127.0.0.1 --db_port 5432 --addons-path odoo-19.0\addons,controle_combustivel\.. -d erp_final
   ```
3. **Acesse**: `http://localhost:8069` (User: `admin` / Pass: `admin`)

---

## 💎 Créditos e Missão
Desenvolvido para **MachadoERP** com foco em transformar dados brutos em decisões estratégicas. O módulo `controle_combustivel` é o estado da arte em extensões customizadas para o ecossistema Odoo.
