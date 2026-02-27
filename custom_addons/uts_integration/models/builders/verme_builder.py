"""
Verme Bildirimi payload üretim mantığı — 3 alt tip:
  - Standart Verme (3.1.4): KUN'lu kuruma
  - Tanımsız Yere Verme (3.1.7): VKN'li firmaya
  - Tüketiciye Verme (3.1.10): Şahıs/son kullanıcıya

Pure Python mixin — Odoo model değil.
"""
import logging
import datetime

_logger = logging.getLogger(__name__)


class VermeBuilderMixin:

    def _build_verme_payloads_from_picking(self, picking):
        """Standart Verme: KUN'u olan kuruma."""
        from odoo import _
        from odoo.exceptions import UserError

        partner = picking.partner_id
        KUN = partner.uts_institution_no or partner.commercial_partner_id.uts_institution_no
        if not KUN:
            raise UserError(_("ÜTS Verme: Müşterinin KUN numarası eksik."))

        payloads = []
        for move, line, data in self._iter_verme_lines(picking, "Verme"):
            self._require_lot_for_verme(data, move.product_id.name, "Verme")

            payload = {
                'UNO': data['uno'],
                'KUN': KUN,
                'BNO': picking.name,
                'BEN': 'HAYIR',
            }
            UDI = getattr(move.product_id, 'uts_udi', None) or None
            if UDI:
                payload['UDI'] = UDI

            self._apply_tracking(payload, data['tracking'], data['lot'], data['qty'])
            payloads.append(payload)

        return payloads

    def _build_tanimsiz_yere_verme_payloads_from_picking(self, picking):
        """Tanımsız Yere Verme: KUN yok, VKN'li firmaya."""
        from odoo import _
        from odoo.exceptions import UserError
        from .base_builder import BNO_MAX

        partner = picking.partner_id
        VKN = (partner.vat or '').strip() or (partner.commercial_partner_id.vat or '').strip()
        if not VKN:
            raise UserError(_(
                "Tanımsız Yere Verme: Müşterinin VKN (Vergi Kimlik No) alanı boş.\n"
                "Lütfen müşteri kartındaki 'Vergi Kimlik Numarası' alanını doldurunuz."
            ))

        payloads = []
        for move, line, data in self._iter_verme_lines(picking, "Tanımsız Yere Verme"):
            self._require_lot_for_verme(data, move.product_id.name, "Tanımsız Yere Verme")

            payload = {
                'UNO': data['uno'],
                'VKN': VKN,
                'BNO': self._cut(picking.name, BNO_MAX),
                'BEN': 'HAYIR',
            }
            self._apply_tracking(payload, data['tracking'], data['lot'], data['qty'])
            payloads.append(payload)

        return payloads

    def _build_tuketiciye_verme_payloads_from_picking(self, picking):
        """Tüketiciye Verme: Şahıs/son kullanıcıya."""
        from odoo import _
        from odoo.exceptions import UserError

        partner = picking.partner_id
        git_date = picking.date_done or datetime.date.today()
        if hasattr(git_date, 'date'):
            git_date = git_date.date()
        GIT = git_date.strftime('%Y-%m-%d')

        payloads = []
        for move, line, data in self._iter_verme_lines(picking, "Tüketici Verme"):
            self._require_lot_for_verme(data, move.product_id.name, "Tüketici Verme")

            payload = {
                'UNO': data['uno'],
                'GIT': GIT,
                'BEN': 'HAYIR',
            }

            tkn = (getattr(partner, 'uts_tc_kimlik_no', None) or '').strip()
            if tkn and len(tkn) == 11 and tkn.isdigit():
                payload['TKN'] = tkn
                payload['TUR'] = 'TC_KIMLIK_NUMARASI_VAR'
                if partner.name:
                    parts = partner.name.strip().split()
                    payload['TUA'] = parts[0] if parts else partner.name
                    payload['TUS'] = ' '.join(parts[1:]) if len(parts) > 1 else ''
            else:
                payload['TUR'] = 'KIMLIGI_BELIRSIZ'

            self._apply_tracking(payload, data['tracking'], data['lot'], data['qty'])
            payloads.append(payload)

        return payloads

    # ------------------------------------------------------------------ #
    # Ortak yardımcılar (sadece Verme builder'ları için)
    # ------------------------------------------------------------------ #

    def _iter_verme_lines(self, picking, label):
        """Çıkış sevkiyatındaki ÜTS-takipli satırları iterate eder."""
        for move in picking.move_ids.filtered(lambda m: m.product_id.is_uts_tracked):
            for line in move.move_line_ids:
                data = self._extract_line_data(move.product_id, line)
                if not data['uno']:
                    _logger.warning("ÜTS %s: UNO eksik (%s), satır atlandı", label, move.product_id.name)
                    continue
                yield move, line, data

    def _require_lot_for_verme(self, data, product_name, label):
        """Lot/Seri numarasının varlığını zorunlu tutar."""
        from odoo import _
        from odoo.exceptions import UserError
        if not data['lot']:
            raise UserError(_(
                "ÜTS %s: '%s' ürünü için Lot/Seri numarası girilmemiş.\n"
                "Lütfen 'Detaylı İşlemler' sekmesinden lot numarasını girin."
            ) % (label, product_name))
