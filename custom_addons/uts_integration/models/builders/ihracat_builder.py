"""
İhracat Bildirimi (3.1.15) payload üretim mantığı.
Pure Python mixin — Odoo model değil.
"""
import logging

_logger = logging.getLogger(__name__)


class IhracatBuilderMixin:

    def _build_ihracat_payloads_from_picking(self, picking):
        """
        İhracat bildirimi payload listesi.
        Zorunlu: UNO, LNO/SNO, ADT (lot), GBN, BEN
        """
        from odoo import _
        from odoo.exceptions import UserError
        from .base_builder import SNO_MAX

        GBN = (picking.uts_gbn or '').strip()
        if not GBN:
            raise UserError(_("İhracat bildirimi için Gümrük Beyanname Numarası (GBN) zorunludur."))

        payloads = []
        for move in picking.move_ids.filtered(lambda m: m.product_id.is_uts_tracked):
            for line in move.move_line_ids:
                data = self._extract_line_data(move.product_id, line)

                if not data['uno']:
                    _logger.warning("ÜTS İhracat: UNO eksik (%s), satır atlandı", move.product_id.name)
                    continue

                if not data['lot']:
                    raise UserError(_(
                        "ÜTS İhracat: '%s' ürünü için Lot/Seri numarası girilmemiş."
                    ) % move.product_id.name)

                payload = {
                    'UNO': data['uno'],
                    'GBN': GBN[:16],
                    'BEN': 'HAYIR',
                }
                self._apply_tracking(payload, data['tracking'], data['lot'], data['qty'])
                payloads.append(payload)

        return payloads
