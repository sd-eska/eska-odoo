from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    uts_institution_no = fields.Char(
        "ÜTS Kurum No (KUN)",
        help="ÜTS'de tanımlı Kurum/Firma Numarası (KUN). Doluysa standart 'verme/ekle' bildirimi yapılır."
    )

    uts_tc_kimlik_no = fields.Char(
        "T.C. Kimlik No",
        help="Tüketici bildirimi için kişinin T.C. Kimlik numarası. 11 haneli olmalıdır."
    )

    uts_verme_turu = fields.Selection([
        ('verme', 'Standart Verme (KUN)'),
        ('tanimsiz', 'Tanımsız Yere Verme (VKN)'),
        ('tuketici', 'Tüketici Verme (Şahıs)'),
    ],
        string="ÜTS Verme Bildirimi Türü",
        compute='_compute_uts_verme_turu',
        store=False,
        help="Otomatik belirlenir: KUN varsa Standart, VKN varsa Tanımsız, ikisi de yoksa Tüketici."
    )

    @api.depends('uts_institution_no', 'vat', 'commercial_partner_id')
    def _compute_uts_verme_turu(self):
        for rec in self:
            kun = rec.uts_institution_no or rec.commercial_partner_id.uts_institution_no
            if kun:
                rec.uts_verme_turu = 'verme'
                continue
            vkn = (rec.vat or '').strip() or (rec.commercial_partner_id.vat or '').strip()
            rec.uts_verme_turu = 'tanimsiz' if vkn else 'tuketici'
