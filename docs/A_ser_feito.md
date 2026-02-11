Vamos criar um sistema usando o framework do python chamado odoo.

O sistema deve ter as seguintes funcionalidades:

Organização e estrutura do código
ferramentas e bibliotecas que tenham(ORM, views e security)
Aplicação de regras simples de negócio
Clareza na explicação do que foi desenvolvido

vamos ultilizar a versão Odoo 19 (Community)

Repositório oficial: https://github.com/odoo/odoo

Documentação (19.0 – PT-BR): https://www.odoo.com/documentation/19.0/pt_BR/applications/general.html



Seu objetivo para este teste é desenvolver um mini-módulo no Odoo Community com foco em estrutura, lógica e organização.

Módulo: controle_combustivel

1) Abastecimentos
Integração com equipamentos/placas cadastrados no Odoo
Campos: equipamento/placa, data e hora, horímetro/odômetro
Litros, valor por litro, total calculado automaticamente
Usuário responsável e motorista

2) Estoque de Combustível (Tanque 6.000 L)
Entradas aumentam o estoque
Abastecimentos reduzem o estoque
Exibição do estoque atual
integração com recebimento de compras

3) Permissões
Motorista: registra abastecimentos sem alterar estoque manualmente
Analista: visualiza relatórios
Administrador: acesso total ao módulo