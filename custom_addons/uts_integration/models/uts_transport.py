import requests
import json
import logging
import odoo
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

# WAF cooldown süresi (saniye) — bakanlık bloğu sonrası bekleme
WAF_COOLDOWN_SECONDS = 120


class UtsTransport(models.AbstractModel):
    _name = 'uts.transport'
    _inherit = 'uts.config.mixin'
    _description = 'ÜTS HTTP Transport'

    # ------------------------------------------------------------------ #
    # WAF Cooldown Yardımcıları
    # ------------------------------------------------------------------ #

    def _is_waf_cooldown_active(self):
        """Son WAF bloğundan beri yeterli süre geçmedi ise True döner."""
        return self._waf_cooldown_remaining() > 0

    def _waf_cooldown_remaining(self):
        """WAF cooldown'dan kalan saniyeyi döner. Aktif değilse 0."""
        last_waf = self.env['uts.log'].sudo().search([
            ('status_code', '=', 403),
        ], order='create_date desc', limit=1)

        if not last_waf:
            return 0

        elapsed = (fields.Datetime.now() - last_waf.create_date).total_seconds()
        remaining = WAF_COOLDOWN_SECONDS - elapsed
        return max(0, int(remaining))

    # ------------------------------------------------------------------ #
    # HTTP POST
    # ------------------------------------------------------------------ #

    def _post(self, endpoint, data, res_model=False, res_id=False):
        """
        Saf HTTP POST katmanı.
        - Payload temizler (boş alanları çıkarır)
        - İsteği gönderir
        - uts.log'a yazar
        - Standart bir sonuç dict'i döner
        """
        url = f"{self._uts_get_base_url()}/{endpoint}"
        headers = self._uts_get_headers()
        payload = {k: v for k, v in data.items() if v not in [None, False, ""]}

        try:
            _logger.info("ÜTS → %s | payload: %s", url, payload)
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            # Ayrı cursor kullan: UserError rollback'i logu silmesin
            self._uts_log_write(endpoint, res_model, res_id, payload, response.text, response.status_code)

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    return {'success': True, 'raw': response.text}

            if response.status_code == 403:
                _logger.warning("ÜTS WAF bloğu algılandı. Cooldown başladı.")
                return {'error': True, 'code': 'WAF_BLOCK', 'message': 'WAF koruması tetiklendi.'}

            return {'error': True, 'code': response.status_code, 'message': response.text}

        except Exception as e:
            _logger.error("ÜTS bağlantı hatası: %s", str(e))
            self._uts_log_write(endpoint, res_model, res_id, payload if 'payload' in dir() else {}, str(e), 0)
            return {'error': True, 'message': f"Bağlantı Hatası: {str(e)}"}

    # ------------------------------------------------------------------ #
    # Log Yazma (Ayrı Cursor — UserError rollback'ten korumalı)
    # ------------------------------------------------------------------ #

    def _uts_log_write(self, endpoint, res_model, res_id, payload, response_text, status_code):
        """
        uts.log kaydını AYRI bir veritabanı cursor'ıyla yazar.
        Bu sayede UserError fırlatılıp ana transaction rollback olsa bile
        log kaydı veritabanında kalıcı olarak saklanır.
        """
        try:
            db_name = self.env.cr.dbname
            with odoo.registry(db_name).cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                new_env['uts.log'].create({
                    'name': endpoint,
                    'res_model': res_model,
                    'res_id': res_id,
                    'request_data': json.dumps(payload, indent=2, ensure_ascii=False),
                    'response_data': str(response_text),
                    'status_code': status_code,
                })
                # new_cr context manager otomatik commit eder
        except Exception as log_err:
            _logger.error("ÜTS log yazma hatası: %s", str(log_err))
