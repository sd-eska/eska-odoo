"""
İade Alma Bildirimleri:
  - Tüketiciden İade Alma (3.1.11)
  - ÜTS'de Tanımsız Yerden İade Alma (3.1.8)

Pure Python mixin — Odoo model değil.
"""
import logging

_logger = logging.getLogger(__name__)


class IadeBuilderMixin:

    def _build_tuketiciden_iade_payloads(self, picking):
        """
        Tüketiciden İade Alma payload listesi.
        Yol 1: Orijinal bildirim BID'si (TID) varsa → TID + ADT
        Yol 2: BID yoksa → UNO + LNO/SNO + ADT
        """
        from odoo import _
        from odoo.exceptions import UserError
        from .base_builder import SNO_MAX

        payloads = []
        for move in picking.move_ids.filtered(lambda m: m.product_id.is_uts_tracked):
            for line in move.move_line_ids:
                data = self._extract_line_data(move.product_id, line)

                if not data['uno']:
                    _logger.warning("ÜTS Tüketiciden İade: UNO eksik (%s), atlandı", move.product_id.name)
                    continue

                # Orijinal verme BID'si var mı?
                bid = self._find_original_bid(line, 'tuketici_verme')

                payload = {}
                if bid:
                    payload['TID'] = bid
                else:
                    payload['UNO'] = data['uno']
                    self._apply_tracking(payload, data['tracking'], data['lot'], data['qty'])

                # Lot bazında ADT zorunlu (TID ile de gönderilebilir)
                if data['tracking'] != 'serial' and data['qty'] > 0 and 'ADT' not in payload:
                    payload['ADT'] = max(1, data['qty'])

                payloads.append(payload)

        return payloads

    def _build_tanimsiz_yerden_iade_payloads(self, picking):
        """
        Tanımsız Yerden İade Alma payload listesi.
        Yol 1: Orijinal bildirim BID'si (UTI) varsa → UTI + ADT
        Yol 2: BID yoksa → UNO + LNO/SNO + ADT
        """
        from .base_builder import SNO_MAX

        payloads = []
        for move in picking.move_ids.filtered(lambda m: m.product_id.is_uts_tracked):
            for line in move.move_line_ids:
                data = self._extract_line_data(move.product_id, line)

                if not data['uno']:
                    _logger.warning("ÜTS Tanımsız Yerden İade: UNO eksik (%s), atlandı", move.product_id.name)
                    continue

                bid = self._find_original_bid(line, 'tanimsiz_verme')

                payload = {}
                if bid:
                    payload['UTI'] = bid
                else:
                    payload['UNO'] = data['uno']
                    self._apply_tracking(payload, data['tracking'], data['lot'], data['qty'])

                if data['tracking'] != 'serial' and data['qty'] > 0 and 'ADT' not in payload:
                    payload['ADT'] = max(1, data['qty'])

                payloads.append(payload)

        return payloads

    # ------------------------------------------------------------------ #
    # Orijinal Bildirim BID Bulma
    # ------------------------------------------------------------------ #

    def _find_original_bid(self, line, bildirim_tipi):
        """
        İade yapılan ürünün orijinal verme bildirimi BID'sini arar.
        Return picking'in origin'inden orijinal picking'i bulur,
        orijinal picking'in move.line'larından BID'yi okur.
        """
        try:
            picking = line.picking_id
            if not picking or not picking.origin:
                return None

            # Return picking'in origin'i → orijinal picking adı
            original_picking = self.env['stock.picking'].search([
                ('name', '=', picking.origin),
            ], limit=1)

            if not original_picking:
                return None

            # Orijinal picking'in move.line'larından eşleşen ürün+lot'u bul
            original_lines = original_picking.move_line_ids.filtered(
                lambda l: l.product_id == line.product_id
                           and l.lot_id == line.lot_id
                           and l.uts_bildirim_kodu
                           and l.uts_bildirimi_tipi == bildirim_tipi
            )
            if original_lines:
                return original_lines[0].uts_bildirim_kodu

        except Exception as e:
            _logger.warning("ÜTS İade: BID aranırken hata: %s", str(e))

        return None
