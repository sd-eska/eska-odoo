# -*- coding: utf-8 -*-
{
    'name': 'Real Estate',
    'version': '1.0',
    'summary': 'Emlak Yönetim Sistemi',
    'description': """
        Emlak Modülü
        ============
        Gayrimenkul yönetimi için:
        - Mülk kayıtları
        - Fiyat takibi
        - Müsaitlik yönetimi
    """,
    'author': 'Odoo Öğrencisi',
    'website': 'https://github.com/suaybdemir',
    'category': 'Real Estate/Brokerage',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/estate_data.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/res_users_views.xml',
        'views/estate_menus.xml',
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'estate/static/src/services/**/*.js',
            'estate/static/src/dashboard_action.js',
            'estate/static/src/components/**/*.js',
            'estate/static/src/components/**/*.xml',
            'estate/static/src/components/**/*.css',
        ],
        'awesome_dashboard.dashboard': [
            'estate/static/src/dashboard/**/*.js',
            'estate/static/src/dashboard/**/*.xml',
            'estate/static/src/dashboard/**/*.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
