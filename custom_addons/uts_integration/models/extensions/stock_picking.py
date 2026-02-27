from odoo import models, fields, _, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'uts.sync.mixin']

    # ================================================================== #
    # ÜTS Alanları
    # ================================================================== #

    uts_verme_tipi = fields.Selection([
        ('standart', 'Standart Verme (KUN)'),
        ('tanimsiz', 'Tanımsız Yere Verme (VKN)'),
        ('tuketici', 'Tüketiciye Verme'),
        ('kozmetik', 'Kozmetik Firmaya Verme'),
        ('ihracat', 'İhracat'),
    ], string="ÜTS Verme Tipi", copy=False,
       help="Boş bırakılırsa müşteri kartına göre otomatik belirlenir.")

    uts_gbn = fields.Char(
        string="Gümrük Beyanname No",
        size=16, copy=False,
        help="İhracat bildirimi için zorunlu (max 16 karakter)."
    )

    uts_iade_tipi = fields.Selection([
        ('tuketiciden_iade', 'Tüketiciden İade Alma'),
        ('tanimsiz_yerden_iade', 'Tanımsız Yerden İade Alma'),
    ], string="ÜTS İade Tipi", copy=False)

    # ================================================================== #
    # Verme Tipi Belirleme
    # ================================================================== #

    def _uts_verme_turu(self):
        """
        Kullanıcı seçimi varsa onu kullan, yoksa partner'a göre otomatik.
        Dönüş: 'standart' | 'tanimsiz' | 'tuketici' | 'kozmetik' | 'ihracat'
        """
        if self.uts_verme_tipi:
            return self.uts_verme_tipi

        # Otomatik belirleme (geriye uyumluluk)
        partner = self.partner_id
        KUN = partner.uts_institution_no or partner.commercial_partner_id.uts_institution_no
        if KUN:
            return 'standart'

        VKN = (partner.vat or '').strip() or (partner.commercial_partner_id.vat or '').strip()
        if VKN:
            return 'tanimsiz'

        return 'tuketici'

    # ================================================================== #
    # Action Butonları
    # ================================================================== #

    def action_uts_verme_bildirimi(self):
        """Tüm verme bildirim tiplerini tek butondan yönetir."""
        self.ensure_one()
        if self.picking_type_id.code != 'outgoing':
            raise UserError(_("Verme bildirimi sadece giden sevkiyatlar için yapılabilir."))
        if self.state != 'done':
            raise UserError(_("Verme bildirimi için sevkiyat 'Bitti' olmalıdır."))

        tur = self._uts_verme_turu()
        METHOD_MAP = {
            'standart': 'verme_bildirimi_ekle',
            'tanimsiz': 'tanimsiz_yere_verme_bildirimi_ekle',
            'tuketici': 'tuketiciye_verme_bildirimi_ekle',
            'kozmetik': 'kozmetik_firmaya_verme_ekle',
            'ihracat':  'ihracat_bildirimi_ekle',
        }

        if tur == 'ihracat' and not self.uts_gbn:
            raise UserError(_("İhracat bildirimi için Gümrük Beyanname Numarası (GBN) zorunludur."))

        method = METHOD_MAP.get(tur)
        if not method:
            raise UserError(_("Bilinmeyen verme tipi: %s") % tur)

        self._send_to_uts(method)
        return True

    def action_uts_alim_bildirimi(self):
        self.ensure_one()
        if self.picking_type_id.code != 'incoming':
            raise UserError(_("Alım bildirimi sadece gelen sevkiyatlar için yapılabilir."))
        if self.state != 'done':
            raise UserError(_("Alım bildirimi için sevkiyat 'Bitti' olmalıdır."))
        self._send_to_uts('alim_bildirimi_ekle')
        return True

    def action_uts_iade_bildirimi(self):
        """İade bildirimi (tüketiciden veya tanımsız yerden)."""
        self.ensure_one()
        if self.state != 'done':
            raise UserError(_("İade bildirimi için sevkiyat 'Bitti' olmalıdır."))
        if not self.uts_iade_tipi:
            raise UserError(_("Lütfen ÜTS İade Tipi seçin (Tüketiciden İade / Tanımsız Yerden İade)."))

        if self.uts_iade_tipi == 'tuketiciden_iade':
            self._send_to_uts('tuketiciden_iade_alma_ekle')
        else:
            self._send_to_uts('tanimsiz_yerden_iade_alma_ekle')
        return True

    # ================================================================== #
    # Payload Üretimi
    # ================================================================== #

    def _prepare_uts_payloads(self):
        code = self.picking_type_id.code
        client = self.env['uts.client']

        if code == 'outgoing':
            tur = self._uts_verme_turu()
            BUILDER_MAP = {
                'standart': client._build_verme_payloads_from_picking,
                'tanimsiz': client._build_tanimsiz_yere_verme_payloads_from_picking,
                'tuketici': client._build_tuketiciye_verme_payloads_from_picking,
                'kozmetik': client._build_kozmetik_verme_payloads_from_picking,
                'ihracat':  client._build_ihracat_payloads_from_picking,
            }
            builder_fn = BUILDER_MAP.get(tur)
            if builder_fn:
                return builder_fn(self)
            return []

        if code == 'incoming':
            # İade işlemi mi yoksa normal alım mı?
            if self.uts_iade_tipi == 'tuketiciden_iade':
                return client._build_tuketiciden_iade_payloads(self)
            elif self.uts_iade_tipi == 'tanimsiz_yerden_iade':
                return client._build_tanimsiz_yerden_iade_payloads(self)
            return client._build_alim_payloads_from_picking(self)

        return []
