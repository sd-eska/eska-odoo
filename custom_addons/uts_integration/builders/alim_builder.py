"""
Alım Bildirimi (3.1.3) payload üretim mantığı.
Pure Python mixin — Odoo model değil.
"""
import logging

_logger = logging.getLogger(__name__)


class AlimBuilderMixin:

    def _build_alim_payloads_from_picking(self, picking):
        """
        Gelen sevkiyattan (stock.picking/incoming) alım bildirimi payload listesi döner.
        """
        from odoo import _
        from odoo.exceptions import UserError
        from .base_builder import SNO_MAX

        payloads = []
        for move in picking.move_ids.filtered(lambda m: m.product_id.is_uts_tracked):
            for line in move.move_line_ids:
                data = self._extract_line_data(move.product_id, line)

                if not data['uno']:
                    _logger.warning("ÜTS Alım: UNO eksik (%s), satır atlandı", move.product_id.name)
                    continue

                if not data['lot']:
                    raise UserError(_(
                        "ÜTS Alım: '%s' ürünü için Lot/Seri numarası girilmemiş.\n"
                        "Lütfen 'Detaylı İşlemler' sekmesinden lot numarasını girin."
                    ) % move.product_id.name)

                payload = {'UNO': data['uno']}

                if data['tracking'] == 'serial':
                    payload['SNO'] = self._cut(data['lot'], SNO_MAX)
                    payload['ADT'] = 1
                else:
                    payload['LNO'] = data['lot']
                    payload['ADT'] = max(1, data['qty'])

                payloads.append(payload)

        return payloads
