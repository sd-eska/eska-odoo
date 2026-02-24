from odoo import models


class UtsClient(models.AbstractModel):
    _name = 'uts.client'
    _inherit = 'uts.transport'
    _description = 'ÜTS Endpoint Tanımları'

    def uretim_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.1 Üretim Bildirimi → uretim/ekle"""
        return self._post('uretim/ekle', vals, res_model, res_id)

    def verme_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.2 Verme Bildirimi → verme/ekle"""
        return self._post('verme/ekle', vals, res_model, res_id)

    def tuketim_bildirimi_ekle(self, vals, res_model=False, res_id=False):
        """3.1.10 Tüketim Bildirimi → tuketim/ekle"""
        return self._post('tuketim/ekle', vals, res_model, res_id)
