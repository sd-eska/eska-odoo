from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'uts.sync.mixin']

    def action_uts_uretim_bildirimi(self):
        """ÜTS'ye üretim bildirimi gönderir (Event-Driven, doğrudan)."""
        self.ensure_one()

        if not self.product_id.is_uts_tracked:
            raise UserError(_("Bu ürün ÜTS takibine tabi değil."))

        if self.state != 'done':
            raise UserError(_("Üretim bildirimi için üretim emrinin 'Bitti' durumunda olması gerekir."))

        self._send_to_uts('uretim_bildirimi_ekle')
        return True

    def _prepare_uts_payloads(self):
        """Tüm üretim hareket satırları için payload listesi üretir."""
        payloads = []
        finished_moves = self.move_finished_ids.filtered(
            lambda m: m.product_id == self.product_id
        )
        for move in finished_moves:
            for line in move.move_line_ids:
                payload = self._build_line_payload(line)
                if payload:
                    payloads.append(payload)
        return payloads

    def _build_line_payload(self, line):
        """
        Tek bir üretim satırı için ÜTS payload'ı oluşturur.
        Zorunlu alanlardan biri eksikse None döner (işlem atlanır, crash olmaz).
        """
        # Guard Clauses: Zorunlu alanlar yoksa bu satırı warning vererek atla
        if not self.product_id.barcode:
            _logger.warning("ÜTS: '%s' ürününde barkod eksik, satır atlandı.", self.product_id.name)
            return None

        # Here we can add our business objectives rules which there is in UTS Documentation
        # ...
        # ..

        uretim_tarihi = self.date_finished or self.date_start
        if not uretim_tarihi:
            _logger.warning("ÜTS: '%s' üretim emrinde tarih yok, satır atlandı.", self.name)
            return None

        payload = {
            "UNO": self.product_id.barcode,
            "URT": fields.Date.to_string(uretim_tarihi),
            "UDI": self.product_id.uts_udi or "",
        }

        if line.lot_id:
            payload.update(self._get_tracking_fields(line))
            payload.update(self._get_expiration_field(line))

        return payload

    def _get_tracking_fields(self, line):
        """
        Ürün takip tipine göre ilgili ÜTS alanlarını döner.
        - serial → SNO + ADT=1
        - lot    → LNO + ADT=miktar
        """
        qty = int(line.quantity or 0)

        if self.product_id.tracking == 'serial':
            return {"SNO": line.lot_id.name, "ADT": 1}
        if self.product_id.tracking == 'lot':
            return {"LNO": line.lot_id.name, "ADT": qty}
        return {"ADT": qty}

    def _get_expiration_field(self, line):
        """
        Son kullanma tarihini (SKT) güvenli şekilde alır.
        'product_expiry' modülü kurulu değilse veya tarih boşsa {} döner.
        """
        try:
            if line.lot_id._fields.get('expiration_date') and line.lot_id.expiration_date:
                return {"SKT": fields.Datetime.to_string(line.lot_id.expiration_date)[:10]}
        except Exception:
            pass
        return {}
