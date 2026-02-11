# Controle de Combustível

<img src="static/description/icon.png" width="100" alt="Ícone do Módulo"/>

Módulo Odoo Community para gerenciamento completo de abastecimento de combustível.

## 📋 Visão Geral

O **Controle de Combustível** é um mini-ERP integrado ao Odoo que permite:

- Registrar e controlar abastecimentos de veículos e equipamentos
- Gerenciar estoque de um tanque de combustível (6.000 litros)
- Visualizar dashboard gerencial com indicadores em tempo real
- Gerar relatórios de consumo por período
- Controlar acesso por perfis de usuário

## ✨ Funcionalidades

### Abastecimentos
- Registro completo de abastecimentos
- Integração com módulo de Frota (fleet)
- Cálculo automático de total
- Validação de estoque antes de confirmar
- Histórico com rastreabilidade (auditoria)

### Controle de Tanque
- Capacidade fixa de 6.000 litros
- Controle de entradas (compras/reposições)
- Indicador visual de nível (verde/amarelo/vermelho)
- Status: Normal (>50%), Atenção (20-50%), Crítico (<20%)

### Dashboard
- Estoque atual com indicador visual
- Consumo e gasto do mês
- Último abastecimento
- Total de abastecimentos do período

### Relatórios
- Lista de abastecimentos com filtros
- Relatório pivot por período
- Gráficos de consumo
- Exportação PDF de comprovantes

## 👥 Perfis de Acesso

| Perfil | Permissões |
|--------|------------|
| **Motorista** | Registrar próprios abastecimentos, visualizar confirmados |
| **Analista** | Visualizar todos os registros, acessar relatórios e dashboard (leitura) |
| **Administrador** | Acesso total, configurar tanque, cancelar registros |

## 🔧 Requisitos

- Odoo Community 16.0 ou superior
- Módulo **Fleet** (Frota) instalado
- Python 3.8+

## 📦 Instalação

1. Copie a pasta `controle_combustivel` para o diretório de addons do Odoo:
   ```bash
   cp -r controle_combustivel /path/to/odoo/addons/
   ```

2. Reinicie o servidor Odoo:
   ```bash
   sudo systemctl restart odoo
   ```

3. Ative o modo desenvolvedor:
   - Configurações → Opções de Desenvolvedor → Ativar modo desenvolvedor

4. Atualize a lista de aplicativos:
   - Aplicativos → Atualizar Lista de Aplicativos

5. Instale o módulo:
   - Busque por "Controle de Combustível" e clique em Instalar

## 🚀 Como Usar

### Primeiro Acesso

1. Acesse o menu **Combustível**
2. Vá em **Tanque → Entradas de Combustível**
3. Registre a primeira entrada para ter estoque

### Registrar Abastecimento

1. Menu **Combustível → Abastecimentos**
2. Clique em **Criar**
3. Preencha os campos obrigatórios:
   - Veículo/Equipamento
   - Quantidade de litros
   - Valor por litro
   - Horímetro/Odômetro
4. Clique em **Confirmar Abastecimento**

### Visualizar Dashboard

1. Menu **Combustível → Dashboard**
2. Visualize os indicadores em tempo real

## ⚙️ Configuração

### Ajustar Estoque Inicial

1. Menu **Combustível → Configuração → Configurar Tanque**
2. Edite o campo "Estoque Inicial" (apenas Administrador)

### Criar Usuários

1. Configurações → Usuários
2. Na aba "Controle de Combustível", selecione o perfil:
   - Motorista
   - Analista
   - Administrador

## 📝 Observações Técnicas

### Estrutura do Módulo

```
controle_combustivel/
├── models/              # Modelos ORM (Python)
├── views/               # Interfaces XML
├── security/            # Grupos e permissões
├── data/                # Dados iniciais
├── reports/             # Templates de relatório
├── controllers/         # Controllers HTTP
└── static/              # CSS e assets
```

### Modelos Principais

- `controle.combustivel.abastecimento` - Registros de abastecimento
- `controle.combustivel.tanque` - Tanque de combustível
- `controle.combustivel.entrada` - Entradas de combustível

### Campos Computados

- **Total**: Calculado automaticamente (quantidade × valor por litro)
- **Estoque atual**: Calculado a partir de entradas e saídas
- **Percentual nível**: Calculado em relação à capacidade

### Validações

- Estoque verificado antes de confirmar abastecimento
- Quantidade e valor devem ser positivos
- Registros confirmados não podem ser excluídos

### Auditoria

O módulo herda de `mail.thread` para rastreamento automático:
- Quem criou o registro
- Quando foi criado
- Histórico de alterações

## 🎨 Customização

### Cores do Tema

| Elemento | Cor |
|----------|-----|
| Primária | `#A43A2F` |
| Background | `#F8F9FA` |
| Texto | `#464A4B` |
| Verde | `#28A745` |
| Amarelo | `#FFC107` |

### Tipografia

- Títulos: Inter Tight, Noto
- Texto: Inter, Noto

## 📄 Licença

LGPL-3

## 👨‍💻 Autor

Machado ERP

---

**Versão**: 16.0.1.0.0
