from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    uts_institution_no = fields.Char(
        "ÜTS Kurum No", 
        help="ÜTS'de tanımlı Kurum/Firma Numarası (KUN)"
    )
