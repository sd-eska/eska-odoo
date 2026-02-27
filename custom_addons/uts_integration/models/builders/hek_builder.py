"""
HEK/Zayiat Bildirimi payload üretim mantığı.
Pure Python mixin — Odoo model değil.
"""
import logging

_logger = logging.getLogger(__name__)


class HekBuilderMixin:

    def _build_hek_payloads_from_scrap(self, scrap):
        """
        Hurda/Fire emrinden (stock.scrap) HEK/Zayiat bildirimi payload listesi döner.
        Kutu ürünlerde (x_product_box=True) BOM satırları üzerinden her alt ürün
        için ayrı payload üretilir.
        """
        from .base_builder import LNO_MAX, DTA_MAX

        product = scrap.product_id
        lot = self._cut(scrap.lot_id.name if scrap.lot_id else None, LNO_MAX)
        qty = int(scrap.scrap_qty or 0)
        tur = getattr(scrap, 'uts_scrap_reason', 'HEK')

        if tur == 'DIGER':
            dta_raw = getattr(scrap, 'uts_description', None) or scrap.name or "Hurda İşlemi"
            dta = self._cut(dta_raw, DTA_MAX)
        else:
            dta = None

        is_box = getattr(product, 'x_product_box', False)

        if is_box:
            return self._build_hek_box_payloads(product, lot, qty, tur, dta)
        else:
            return self._build_hek_single_payload(product, lot, qty, tur, dta)

    def _build_hek_single_payload(self, product, lot, qty, tur, dta):
        """Tekil ürün veya lot ürün için tek payload."""
        uno = self._get_uno(product)
        if not uno or not lot or qty <= 0:
            _logger.warning("ÜTS HEK: UNO/LNO/ADT eksik (%s)", product.name)
            return []
        payload = {'UNO': uno, 'LNO': lot, 'ADT': max(1, qty), 'TUR': tur}
        if tur == 'DIGER' and dta:
            payload['DTA'] = dta
        return [payload]

    def _build_hek_box_payloads(self, product, lot, qty, tur, dta):
        """Kutu ürün: BOM'dan alt ürünlerin her biri için ayrı payload."""
        bom_lines = self.env['mrp.bom.line'].search([
            ('product_id', '=', product.id),
            ('x_studio_field_Ml87v', 'in', ['Lot', 'SIP']),
        ])
        payloads = []
        for bl in bom_lines:
            uno = self._normalize_uno(getattr(bl, 'x_product_barcode', None))
            if not uno:
                continue
            bom_qty = int(max(1, round(qty * float(bl.product_qty or 1))))
            p = {'UNO': uno, 'LNO': lot, 'ADT': bom_qty, 'TUR': tur}
            if tur == 'DIGER' and dta:
                p['DTA'] = dta
            payloads.append(p)
        return payloads
