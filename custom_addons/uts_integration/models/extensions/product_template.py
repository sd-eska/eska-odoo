from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_uts_tracked = fields.Boolean("ÜTS Takibi", default=False)
    uts_tracking_type = fields.Selection([
        ('lot', 'Lot'),
        ('serial', 'Seri Numarası'),
        ('sip', 'SİP (Set)'),
        ('yok', 'Yok (Sadece Kutu)'),
    ], string="ÜTS Takip Tipi")
    uts_udi = fields.Char("ÜTS Eşsiz Kimlik (UDI)")
