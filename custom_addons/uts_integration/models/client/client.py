from odoo import models


class UtsClient(models.AbstractModel):
    """
    Katman 4: ÜTS Endpoint Tanımları.
    Sadece endpoint adlarını bilir; payload/transport mantığı yoktur.

    Miras zinciri:
        uts.config.mixin → uts.transport → uts.base.builder
        → uts.payload.mixin → uts.client
    """
    _name = 'uts.client'
    _inherit = 'uts.payload.mixin'
    _description = 'ÜTS Endpoint Tanımları'

    # ================================================================== #
    # Bildirim Ekleme Endpoint'leri
    # ================================================================== #

    def uretim_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.1 Üretim Bildirimi"""
        return self._post('uretim/ekle', vals, res_model, res_id)

    def verme_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.4 Verme Bildirimi (KUN olan kuruma)"""
        return self._post('verme/ekle', vals, res_model, res_id)

    def tanimsiz_yere_verme_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.7 ÜTS'de Tanımsız Yere Verme Bildirimi"""
        return self._post('utsdeTanimsizYereVerme/ekle', vals, res_model, res_id)

    def tuketiciye_verme_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.10 Tüketiciye Verme Bildirimi"""
        return self._post('tuketiciyeVerme/ekle', vals, res_model, res_id)

    def kozmetik_firmaya_verme_ekle(self, vals, res_model=False, res_id=False):
        """3.1.5 Kozmetik Firmaya Verme Bildirimi"""
        return self._post('kozmetikFirmayaVerme/ekle', vals, res_model, res_id)

    def alim_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.3 Alım Bildirimi"""
        return self._post('alma/ekle', vals, res_model, res_id)

    def ihracat_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.15 İhracat Bildirimi"""
        return self._post('ihracat/ekle', vals, res_model, res_id)

    def hek_zayiat_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.17 HEK/Zayiat Bildirimi"""
        return self._post('hekZayiat/ekle', vals, res_model, res_id)

    # ================================================================== #
    # İade Alma Endpoint'leri
    # ================================================================== #

    def tuketiciden_iade_alma_ekle(self, vals, res_model=False, res_id=False):
        """3.1.11 Tüketiciden İade Alma Bildirimi"""
        return self._post('tuketicidenIadeAlma/ekle', vals, res_model, res_id)

    def tanimsiz_yerden_iade_alma_ekle(self, vals, res_model=False, res_id=False):
        """3.1.8 ÜTS'de Tanımsız Yerden İade Alma Bildirimi"""
        return self._post('utsdeTanimsizYerdenIadeAlma/ekle', vals, res_model, res_id)

    # ================================================================== #
    # Sorgulama Endpoint'leri
    # ================================================================== #

    def bildirim_sorgula(self, vals):
        """3.4.9 Bildirim Sorgula (offset parametreli)"""
        return self._post('bildirim/sorgula/offset', vals, False, False)

    def kabul_bekleyenler_sorgula(self, vals):
        """3.4.11 Kabul Edilecek Tekil Ürün Sorgula (offset parametreli)"""
        return self._post('alma/bekleyenler/sorgula/offset', vals, False, False)

    def tekil_urun_bekleyenler_sorgula(self, vals):
        """3.4.12 Tekil Ürün Bilgileri ile Kabul Edilecek Tekil Ürün Sorgula"""
        return self._post('alma/bekleyenler/sorgula/tekilUrun/offset', vals, False, False)
