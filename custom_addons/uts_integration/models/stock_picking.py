from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# ÜTS API sabit değerleri
UTS_BEN_DEFAULT = "HAYIR"


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'uts.sync.mixin']

    def action_uts_verme_bildirimi(self):
        """ÜTS'ye verme bildirimi gönderir (Event-Driven, doğrudan)."""
        self.ensure_one()

        if self.picking_type_id.code != 'outgoing':
            raise UserError(_("Verme bildirimi sadece giden sevkiyatlar için yapılabilir."))

        if self.state != 'done':
            raise UserError(_("Verme bildirimi için sevkiyatın 'Bitti' durumunda olması gerekir."))

        if not self.partner_id.uts_institution_no:
            raise UserError(_("Müşterinin ÜTS Kurum Numarası (KUN) eksik."))

        self._send_to_uts('verme_bildirimi_ekle')
        return True

    def _prepare_uts_payloads(self):
        """Tüm hareket satırları için payload listesi üretir."""
        payloads = []
        uts_moves = self.move_ids.filtered(lambda m: m.product_id.is_uts_tracked)

        for move in uts_moves:
            for line in move.move_line_ids:
                payload = self._build_line_payload(move, line)
                if payload:
                    payloads.append(payload)

        return payloads

    def _build_line_payload(self, move, line):
        """
        Tek bir hareket satırı için ÜTS payload'ı oluşturur.
        Zorunlu alanlardan biri eksikse None döner (işlem atlanır, crash olmaz).
        """
        # Guard Clauses: Zorunlu alanlar yoksa bu satırı warning ile atla
        if not move.product_id.barcode:
            _logger.warning("ÜTS: '%s' ürününde barkod eksik, satır atlandı.", move.product_id.name)
            return None
        if not self.partner_id.uts_institution_no:
            _logger.warning("ÜTS: '%s' müşterisinde KUN eksik, satır atlandı.", self.partner_id.name)
            return None
        if not self.date_done:
            _logger.warning("ÜTS: '%s' sevkiyatında teslim tarihi yok, satır atlandı.", self.name)
            return None

        # Here we can modify our business objectives rules which there is in UTS Documentation
        # ...
        # ..
        # .

        payload = {
            "UNO": move.product_id.barcode,
            "KUN": self.partner_id.uts_institution_no,
            "BNO": self.name,
            "GIT": fields.Date.to_string(self.date_done),
            "BEN": UTS_BEN_DEFAULT,
            "UDI": move.product_id.uts_udi or "",
        }

        payload.update(self._get_tracking_fields(move.product_id, line))
        return payload

    def _get_tracking_fields(self, product, line):
        """
        Ürün takip tipine göre ilgili ÜTS alanlarını döner.
        - serial → SNO + ADT=1
        - lot    → LNO + ADT=miktar
        - none   → sadece ADT=miktar
        """
        qty = int(line.quantity or 0)

        if product.tracking == 'serial':
            return {"SNO": line.lot_id.name, "ADT": 1}
        if product.tracking == 'lot':
            return {"LNO": line.lot_id.name, "ADT": qty}
        return {"ADT": qty}
