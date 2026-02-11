# -*- coding: utf-8 -*-
{
    'name': 'Controle de Combustível',
    'version': '19.0.1.0.0',
    'category': 'Fleet',
    'summary': 'Gerenciamento de abastecimento de combustível',
    'description': """
Controle de Combustível
=======================

Mini-ERP para controle de abastecimentos de combustível, com:

* Registro de abastecimentos
* Controle de estoque de tanque (6.000 litros)
* Dashboard gerencial
* Relatórios de consumo
* Integração com módulo de Frota

Desenvolvido seguindo as melhores práticas Odoo Community.
    """,
    'author': 'Machado ERP',
    'website': 'https://github.com/machado-erp',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'fleet',
        'mail',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequence_data.xml',
        'data/tanque_data.xml',
        
        # Views
        'views/tanque_views.xml',
        'views/abastecimento_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
        
        # Reports
        'reports/report_abastecimento.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'controle_combustivel/static/src/css/dashboard.css',
            # 'controle_combustivel/static/src/js/dashboard.js',
            # 'controle_combustivel/static/src/xml/dashboard.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
