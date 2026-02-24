# -*- coding: utf-8 -*-
{
    'name': 'Estate Accounting',
    'version': '1.0',
    'category': 'Real Estate/Accounting',
    'summary': 'Link between Estate and Account modules',
    'description': """
        This module links the real estate module with accounting.
        It allows for invoice generation when a property is sold.
    """,
    'depends': [
        'estate',
        'account',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
