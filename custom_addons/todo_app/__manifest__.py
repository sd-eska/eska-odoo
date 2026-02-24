# -*- coding: utf-8 -*-
{
    'name': 'Todo App',
    'version': '1.0',
    'summary': 'Simple Todo App',
    'description': """
        İlk Odoo modülü
        ================
        Basit todo:
        - Task oluşturma
        - Task tamamlama
        - Priority belirleme
    """,
    'author': 'Odoo Öğrencisi',
    'website': 'https://github.com/suaybdemir',
    'category': 'Productivity',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/todo_views.xml',
        'views/mymodel_views.xml',
        'views/mymodel_menu.xml',  # Menu loaded after views/actions
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
