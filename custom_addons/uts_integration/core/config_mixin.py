from odoo import models, api, _
from odoo.exceptions import UserError


class UtsConfigMixin(models.AbstractModel):
    """
    Katman 1: ÜTS Yapılandırma.
    URL ve Token okuma sorumluluğu bu katmandadır.
    """
    _name = 'uts.config.mixin'
    _description = 'ÜTS Yapılandırma'

    def _uts_get_base_url(self):
        is_test = self.env['ir.config_parameter'].sudo().get_param('uts.test_mode', default='True')
        if str(is_test).lower() in ('true', '1', 'yes', 't'):
            return "https://utstest.saglik.gov.tr/UTS/uh/rest/bildirim"
        return "https://utsuygulama.saglik.gov.tr/UTS/uh/rest/bildirim"

    def _uts_get_headers(self):
        token = self.env['ir.config_parameter'].sudo().get_param('uts.token')
        if not token:
            raise UserError(_("ÜTS Token bulunamadı. Lütfen Sistem Parametrelerini kontrol edin!"))
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'utsToken': token,
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        }
