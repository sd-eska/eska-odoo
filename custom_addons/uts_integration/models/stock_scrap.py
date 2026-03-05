from odoo import models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockScrap(models.Model):
    _name = 'stock.scrap'
    _inherit = ['stock.scrap', 'uts.sync.mixin']

    uts_scrap_reason = fields.Selection([
        ('HEK', 'HEK'),
        ('DOGAL_AFET', 'Doğal Afet'),
        ('YANGIN', 'Yangın'),
        ('CALINMA', 'Çalınma'),
        ('STOK_DUZELTME', 'Stok Düzeltme'),
        ('DIGER', 'Diğer')
    ], string="Zayiat Nedeni (Seçim)", default="DIGER", required=True)

    uts_description = fields.Char(string="Diğer Zayiat Açıklaması", 
                                  help="Eğer Zayiat Nedeni 'Diğer' ise bu alanı doldurmanız zorunludur.")

    def action_uts_hek_bildirimi(self):
        self.ensure_one()
        if not self.product_id.is_uts_tracked:
            raise UserError(_("Bu ürün ÜTS takibine tabi değil."))
        if self.state != 'done':
            raise UserError(_("HEK/Zayiat bildirimi için hurda işleminin 'Bitti' durumunda olması gerekir."))
        
        tur = getattr(self, 'uts_scrap_reason', 'HEK')
        if tur == 'DIGER':
            if not self.uts_description:
                 raise UserError(_("Lütfen 'Zayiat Nedeni' bölümünde 'Diğer' seçtiğiniz için alttaki açıklama kutusunu doldurunuz."))
        
        self._send_to_uts('hek_zayiat_bildirimi_ekle')
        return True

    def _prepare_uts_payloads(self):
        return self.env['uts.client']._build_hek_payloads_from_scrap(self)
