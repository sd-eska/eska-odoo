{
    'name': 'ÜTS Entegrasyonu',
    'version': '3.0',
    'category': 'Inventory/Manufacturing',
    'summary': 'Ürün Takip Sistemi (ÜTS) Entegrasyonu',
    'description': """
        ÜTS (Ürün Takip Sistemi) ile Odoo arasındaki native entegrasyonu sağlar.
        Event-driven mimari: buton tıklamaları doğrudan API çağrısı yapar.

        Desteklenen bildirim tipleri:
        - Üretim Bildirimi (3.1.1)              — mrp.production
        - Verme Bildirimi (3.1.4)               — stock.picking (outgoing)
        - Tanımsız Yere Verme (3.1.7)           — stock.picking (outgoing)
        - Tüketiciye Verme (3.1.10)             — stock.picking (outgoing)
        - Kozmetik Firmaya Verme (3.1.5)        — stock.picking (outgoing)
        - İhracat Bildirimi (3.1.15)            — stock.picking (outgoing)
        - Alım Bildirimi (3.1.3)                — stock.picking (incoming)
        - Tüketiciden İade Alma (3.1.11)        — stock.picking (incoming/return)
        - Tanımsız Yerden İade Alma (3.1.8)     — stock.picking (incoming/return)
        - HEK/Zayiat (3.1.17)                   — stock.scrap
        - Bildirim Sorgula (3.4.9)              — wizard

        Mimari:
        core/       → HTTP transport + loglama
        builders/   → Payload builder mixin'leri (bildirim başına dosya)
        validators/ → Alan kuralları + hata kodu çevirisi
        client/     → ÜTS endpoint tanımları
        engine/     → Gönderim motoru (pipeline)
        extensions/ → Odoo model genişletmeleri + wizard
    """,
    'author': 'Suayb Demir',
    'depends': ['base', 'product', 'stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
        'data/uts_cron_data.xml',
        'views/uts_config_views.xml',
        'views/product_views.xml',
        'views/mrp_production_views.xml',
        'views/stock_picking_views.xml',
        'views/res_partner_views.xml',
        'views/stock_scrap_views.xml',
        'views/stock_move_line_views.xml',
        'views/uts_bildirim_sorgu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
