from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_uts_tracked = fields.Boolean("ÜTS", default=False)
    uts_tracking_type = fields.Selection([
        ('TEKIL', 'Tekil Takip (SNO)'),
        ('LOT', 'Lot Takip (LNO)')
    ], string="ÜTS Takip Tipi")
    uts_udi = fields.Char("ÜTS Eşsiz Kimlik (UDI)")
