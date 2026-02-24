{
    'name': 'ÜTS Entegrasyonu',
    'version': '1.0',
    'category': 'Inventory/Manufacturing',
    'summary': 'Ürün Takip Sistemi (ÜTS) Entegrasyonu',
    'description': """
        ÜTS (Ürün Takip Sistemi) ile Odoo arasındaki entegrasyonu yönetir.
        - Üretim Bildirimi
        - Verme Bildirimi
        - Rate Limit ve WAF Koruması için Arka Plan Kuyruk İşleme
    """,
    'author': 'Antigravity',
    'depends': ['base', 'product', 'stock', 'mrp', 'stock_sms'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
        'data/uts_cron_data.xml',
        'views/uts_config_views.xml',
        'views/product_views.xml',
        'views/mrp_production_views.xml',
        'views/stock_picking_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
