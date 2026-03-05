"""
Üretim Bildirimi (3.1.1) payload üretim mantığı.

Pure Python mixin — Odoo model değil.
`self` buraya geldiğinde uts.payload.mixin instance'ı olacak,
yani `self.env`, `self._get_uno()` vb. tam çalışır.
"""
import logging

_logger = logging.getLogger(__name__)


class UretimBuilderMixin:

    def _build_uretim_payloads_from_production(self, production):
        """
        Üretim emrinden (mrp.production) tüm move satırlarını okur
        ve ÜTS üretim bildirimi payload listesi döner.
        SİP ürünlerde consume_line_ids üzerinden çocuklar eklenir.
        """
        from odoo import _
        from odoo.exceptions import UserError
        from .base_builder import LNO_MAX, SNO_MAX

        payloads = []
        finished_moves = production.move_finished_ids.filtered(
            lambda m: m.product_id == production.product_id
        )

        for move in finished_moves:
            for line in move.move_line_ids:
                product = production.product_id
                data = self._extract_line_data(product, line)

                if data['tracking'] == 'yok':
                    _logger.info("ÜTS Üretim: tracking=Yok, satır atlandı (%s)", product.name)
                    continue

                if not data['uno']:
                    _logger.warning("ÜTS Üretim: UNO bulunamadı (%s), satır atlandı", product.name)
                    continue

                # URT (Üretim Tarihi) — ZORUNLU
                URT = self._fmt_date(
                    getattr(line.lot_id, 'use_date', None)
                    or production.date_finished
                    or production.date_start
                )
                if not URT:
                    raise UserError(_(
                        "ÜTS Üretim: '%s' ürünü için Üretim Tarihi (URT) bulunamadı.\n"
                        "Üretim emrini tamamladıktan sonra tekrar deneyin."
                    ) % product.name)

                SKT = self._fmt_date(getattr(line.lot_id, 'expiration_date', None))

                payload = {'UNO': data['uno'], 'URT': URT}
                self._apply_tracking(payload, data['tracking'], data['lot'], data['qty'])

                UDI = self._build_udi(data['uno'], URT, data['lot'], SKT)
                if UDI:
                    payload['UDI'] = UDI
                if SKT:
                    payload['SKT'] = SKT

                # SİP çocukları
                if data['tracking'] == 'sip':
                    consume_lines = getattr(
                        line, 'consume_line_ids',
                        production.env['stock.move.line'].browse([])
                    )
                    sip_children = self._build_sip_children(consume_lines, line.quantity or 1)
                    if sip_children:
                        payload['SIP'] = sip_children
                    else:
                        _logger.warning("ÜTS SİP: consume_line_ids boş (move_line: %s)", line.id)

                payloads.append(payload)

        return payloads
