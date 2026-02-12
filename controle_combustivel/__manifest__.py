# -*- coding: utf-8 -*-
{
    'name': 'Controle de Combustível',
    'version': '1.0',
    'category': 'Fleet',
    'summary': 'Gestão de abastecimento e estoque de combustível',
    'description': """
Módulo para controle de abastecimentos de frota, gestão de estoque em tanque e dashboard de performance.
Desenvolvido para MachadoERP.
    """,
    'author': 'Machado ERP',
    'website': 'https://github.com/machado-erp',
    'license': 'LGPL-3',
    'depends': ['base', 'fleet', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/tanque_data.xml',
        'views/tanque_views.xml',
        'views/abastecimento_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
        'reports/report_abastecimento.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'controle_combustivel/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'sequence': 1,
}
