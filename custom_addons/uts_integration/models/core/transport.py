import requests
import json
import logging
import odoo
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class UtsTransport(models.AbstractModel):
    """
    Katman 2: ÜTS HTTP Transport.
    Sadece HTTP POST gönderme ve loglama sorumluluğu vardır.
    """
    _name = 'uts.transport'
    _inherit = 'uts.config.mixin'
    _description = 'ÜTS HTTP Transport'

    def _post(self, endpoint, data, res_model=False, res_id=False):
        """
        Saf HTTP POST katmanı.
        - Boş/None/False alanları temizler
        - İsteği gönderir
        - uts.log'a ayrı cursor ile yazar (UserError rollback'ten korumalı)
        """
        url = f"{self._uts_get_base_url()}/{endpoint}"
        headers = self._uts_get_headers()
        payload = {k: v for k, v in data.items() if v not in [None, False, ""]}

        try:
            _logger.info("ÜTS → %s | payload: %s", url, payload)
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            self._uts_log_write(endpoint, res_model, res_id, payload, response.text, response.status_code)

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    return {'ok': True, 'raw': response.text}

            return {'error': True, 'code': response.status_code, 'message': response.text}

        except Exception as e:
            _logger.error("ÜTS bağlantı hatası: %s", str(e))
            self._uts_log_write(endpoint, res_model, res_id, payload, str(e), 0)
            return {'error': True, 'code': 0, 'message': f"Bağlantı Hatası: {str(e)}"}

    def _uts_log_write(self, endpoint, res_model, res_id, payload, response_text, status_code):
        """
        uts.log kaydını AYRI bir veritabanı cursor'ıyla yazar.
        UserError → rollback olsa bile log kalıcı olarak saklanır.
        """
        try:
            with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                new_env['uts.log'].create({
                    'name': endpoint,
                    'res_model': res_model,
                    'res_id': res_id,
                    'request_data': json.dumps(payload, indent=2, ensure_ascii=False),
                    'response_data': str(response_text),
                    'status_code': status_code,
                })
        except Exception as log_err:
            _logger.error("ÜTS log yazma hatası: %s", str(log_err))
