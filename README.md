# ⛽ MachadoERP - Controle de Combustível (Odoo 19.0)

![Odoo Version](https://img.shields.io/badge/Odoo-19.0%20(Master)-714B67?logo=odoo&logoColor=white)
![Status](https://img.shields.io/badge/Status-Desenvolvimento%20/%20Teste-brightgreen)
![Company](https://img.shields.io/badge/Empresa-MachadoERP-blue)

Este repositório contém o projeto de implementação e teste do módulo de **Controle de Combustível** para a **MachadoERP**, desenvolvido sobre a plataforma Odoo 19.0.

---

## 📋 Sobre o Projeto

O objetivo deste projeto é fornecer uma solução robusta para o gerenciamento de abastecimento de frotas, permitindo o controle rigoroso de estoque de tanques, monitoramento de consumo por motorista e integração com o módulo nativo de Frota (*Fleet*) do Odoo.

### Principais Funcionalidades:
- ✅ **Gestão de Abastecimentos:** Registro detalhado de cada litro consumido.
- ✅ **Controle de Tanque:** Monitoramento em tempo real do nível do tanque (capacidade de 6.000 litros).
- ✅ **Segurança Hierárquica:** Papéis definidos para Motoristas, Analistas e Administradores (usando o novo sistema de *Privileges* do Odoo 19).
- ✅ **Dashboard Dinâmico:** Visualização analítica do consumo e níveis de combustível.
- ✅ **Relatórios Gerenciais:** Geração de PDFs para conferência de abastecimentos.

---

## 🛠️ Stack Técnica e Ambiente

- **Plataforma:** Odoo 19.0 Community (Master Branch)
- **Linguagem:** Python 3.13+
- **Banco de Dados:** PostgreSQL 17+
- **Sistema Operacional:** Windows (Ambiente de Desenvolvimento Local)

### Ajustes Críticos Realizados:
- **Patch de Core:** Correção de bug de inicialização do GeoIP no Odoo 19.
- **Configuração de Locale:** Ajuste de colação de banco de dados para compatibilidade total com o sistema de arquivos Windows.
- **Manifest Refactoring:** Otimização da ordem de carregamento de XML para garantir a integridade das ações de menu.

---

## 🚀 Como Iniciar o Ambiente

O projeto já está configurado e pronto para girar. Siga as instruções abaixo:

1. **Ative o Ambiente Virtual:**
   ```powershell
   .\odoo-venv\Scripts\activate
   ```

2. **Suba o Servidor:**
   ```powershell
   .\odoo-venv\Scripts\python.exe odoo-19.0\odoo-bin -r odoo -w odoo --db_host 127.0.0.1 --db_port 5432 --addons-path odoo-19.0\addons,controle_combustivel\.. -d erp_final --limit-time-real=3600
   ```

3. **Acesse via Navegador:**
   - Link: [http://127.0.0.1:8069/web/login?db=erp_final](http://127.0.0.1:8069/web/login?db=erp_final)
   - Usuário: `admin`
   - Senha: `admin`

---

## 📂 Estrutura do Repositório

```text
MachadoERP-Test/
├── controle_combustivel/    # Módulo customizado (Odoo Addon)
│   ├── data/                # Dados iniciais e sequências
│   ├── models/              # Lógica de negócio (Python)
│   ├── reports/             # Definições de relatórios PDF
│   ├── security/            # Grupos, Privilégios e Regras de Acesso
│   ├── static/              # Ativos (CSS e Imagens)
│   └── views/               # Interfaces de usuário (XML)
├── odoo-19.0/               # Core do Odoo customizado/patcheado
├── odoo-venv/               # Ambiente virtual Python
├── anotações.md             # Notas rápidas de desenvolvimento
└── prompt1.md               # Requisitos originais do projeto
```

---

## 💎 Créditos

Desenvolvido para **MachadoERP**. 
*O foco deste repositório é garantir a qualidade técnica e a inovação no uso das ferramentas Odoo de última geração.*
