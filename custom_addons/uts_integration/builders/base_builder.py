from odoo import models, fields
import logging
import re

_logger = logging.getLogger(__name__)

# ÜTS Doküman Limitleri
UNO_MAX = 23
LNO_MAX = 20
SNO_MAX = 20
DTA_MAX = 50
BNO_MAX = 50


class UtsBaseBuilder(models.AbstractModel):
    """
    Tüm ÜTS builder'larının ortak atasıdır.

    Sorumluluklar:
      - UNO çözümleme (barkod öncelik zinciri)
      - Takip tipi belirleme (serial / lot / sip / yok)
      - Tarih formatlama
      - UDI üretme (GS1)
      - Serial/Lot ayrımını payload'a uygulama

    Alt sınıflar (uretim_builder, verme_builder vb.) sadece
    kendi payload yapılandırmasını ve kaynak okuma mantığını tanımlar.
    """
    _name = 'uts.base.builder'
    _inherit = 'uts.transport'
    _description = 'ÜTS Ortak Payload Builder'

    # ================================================================== #
    # Düşük Seviye Yardımcılar
    # ================================================================== #

    def _cut(self, value, max_len):
        """Değeri belirli uzunluğa keser, boşsa None döner."""
        if not value:
            return None
        return str(value).strip()[:max_len]

    def _fmt_date(self, value):
        """Tarih değerini YYYY-AA-GG string'e çevirir."""
        if not value:
            return None
        try:
            return fields.Date.to_string(value) if hasattr(value, 'year') else str(value)[:10]
        except Exception:
            return None

    def _normalize_uno(self, raw):
        """Barkodu UNO formatına normalize et (max 23 karakter)."""
        if not raw:
            return None
        s = str(raw).strip()
        digits = re.sub(r'\D+', '', s)
        return (digits if digits else s)[:UNO_MAX] or None

    # ================================================================== #
    # Alan Okuma (Odoo Record → Saf Değer)
    # ================================================================== #

    def _get_uno(self, product, line=None):
        """
        UNO öncelik zinciri:
          1. line.x_studio_barkod  (satır bazında özel barkod)
          2. product.x_studio_barkod
          3. product.barcode
        """
        for raw in [
            getattr(line, 'x_studio_barkod', None) if line else None,
            getattr(product, 'x_studio_barkod', None),
            getattr(product, 'barcode', None),
        ]:
            uno = self._normalize_uno(raw)
            if uno:
                return uno
        return None

    def _get_tracking(self, product, line=None):
        """
        Takip tipini belirle:
          - x_product_urun_takip_tipi == 'SIP' → 'sip'
          - x_product_urun_takip_tipi Yok/None → 'yok'
          - product.tracking → 'serial' / 'lot'
        """
        if line:
            tip = str(getattr(line, 'x_product_urun_takip_tipi', '') or '').strip().lower()
            if tip == 'sip':
                return 'sip'
            if tip in ('yok', 'none', 'hayır', 'hayir', 'no'):
                return 'yok'
        tracking = str(getattr(product, 'tracking', '') or '').lower()
        if tracking in ('serial', 'lot'):
            return tracking
        return 'unknown'

    def _extract_line_data(self, product, line):
        """
        Her builder'ın ihtiyaç duyduğu ortak alanları tek seferde çıkarır.
        Dönen dict: {uno, tracking, lot, qty}
        """
        return {
            'uno': self._get_uno(product, line),
            'tracking': self._get_tracking(product, line),
            'lot': self._cut(line.lot_id.name if line.lot_id else None, LNO_MAX),
            'qty': int(line.quantity or 0),
        }

    # ================================================================== #
    # Payload Parça Üreticileri
    # ================================================================== #

    def _apply_tracking(self, payload, tracking, lot, qty):
        """
        Serial/Lot ayrımını payload'a uygular.
        Tekil (serial): SNO verilir, ADT verilmez.
        Lot: LNO + ADT zorunlu.
        """
        if tracking == 'serial':
            payload['SNO'] = self._cut(lot, SNO_MAX)
        else:
            payload['LNO'] = lot
            payload['ADT'] = max(1, qty)

    def _build_udi(self, uno, urt, lno, skt=None):
        """GS1 tabanlı UDI: 010{UNO}11{YYMMDD}[17{YYMMDD}]10{LNO}"""
        if not (uno and urt and lno):
            return None
        try:
            udi = f"010{uno}11{urt.replace('-','')[2:]}"
            if skt:
                udi += f"17{skt.replace('-','')[2:]}"
            return udi + f"10{lno}"
        except Exception:
            return None

    def _build_sip_children(self, consume_lines, parent_qty):
        """
        SİP ürünlerin hammadde satırlarından çocuk kalemleri üretir.
        Aynı UNO+LNO biriktirilir.
        """
        parent_qty = max(1.0, float(parent_qty or 1))
        lot_totals = {}
        serial_items = []

        for line in consume_lines:
            tracking = self._get_tracking(line.product_id, line)
            if tracking == 'yok':
                continue

            UNO = self._get_uno(line.product_id, line)
            if not UNO:
                continue

            lot_name = self._cut(line.lot_id.name if line.lot_id else None, LNO_MAX)

            if tracking == 'serial':
                if lot_name:
                    serial_items.append({'UNO': UNO, 'SNO': lot_name})
                continue

            if not lot_name:
                continue

            adt = max(0, round(float(line.quantity or 0) / parent_qty))
            if adt <= 0:
                continue

            key = f"{UNO}|{lot_name}"
            if key not in lot_totals:
                lot_totals[key] = {'UNO': UNO, 'LNO': lot_name, 'ADT': 0}
            lot_totals[key]['ADT'] += adt

        return list(lot_totals.values()) + serial_items
