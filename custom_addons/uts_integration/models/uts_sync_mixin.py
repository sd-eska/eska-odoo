from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class UtsSyncMixin(models.AbstractModel):
    _name = 'uts.sync.mixin'
    _description = 'ÜTS Senkronizasyonu'

    uts_sync_state = fields.Selection([
        ('draft', 'Gönderilmedi'),
        ('sent', 'Gönderildi'),
        ('failed', 'Hata'),
    ], string="ÜTS Bildirim Durumu", default='draft', copy=False)

    uts_last_response = fields.Text("ÜTS Yanıtı", readonly=True, copy=False)

    def _send_to_uts(self, method_name):
        """
        WAF cooldown aktifse kullanıcıya bilgi verir.
        """
        self.ensure_one()
        client = self.env['uts.client']

        # WAF Cooldown Kontrolü: Son 2 dakikada block yenildiyse dur
        if client._is_waf_cooldown_active():
            remaining = client._waf_cooldown_remaining()
            raise UserError(_(
                "ÜTS Güvenlik Duvarı (WAF) koruması aktif.\n"
                "Lütfen yaklaşık %d saniye bekledikten sonra tekrar deneyin."
            ) % remaining)

        payloads = self._prepare_uts_payloads()

        if not payloads:
            # Tam olarak neyin eksik olduğunu tespit et
            missing = []
            if not self.product_id.barcode:
                missing.append("• Ürün Barkodu (UNO) girilmemiş")
            uretim_tarihi = self.date_finished or self.date_start
            if not uretim_tarihi:
                missing.append("• Üretim / Başlangıç tarihi bulunamadı")
            finished_moves = self.move_finished_ids.filtered(
                lambda m: m.product_id == self.product_id
            )
            has_lines = any(m.move_line_ids for m in finished_moves)
            if not has_lines:
                missing.append("• Bitmiş ürün hareket satırı (move line) bulunamadı")

            detail = "\n".join(missing) if missing else "Bilinmeyen neden."
            raise UserError(_(
                "ÜTS için gönderilecek geçerli veri bulunamadı.\n\n%s"
            ) % detail)

        success_count = 0
        last_error = ""

        for payload in payloads:
            result = getattr(client, method_name)(payload, self._name, self.id)

            if isinstance(result, dict) and result.get('error'):
                if result.get('code') == 'WAF_BLOCK':
                    # WAF bloğu alındı: durumu kaydet, kullanıcıya bildir
                    self.write({
                        'uts_sync_state': 'failed',
                        'uts_last_response': 'WAF koruması tetiklendi. 2 dakika sonra tekrar deneyin.',
                    })
                    raise UserError(_(
                        "ÜTS Güvenlik Duvarı isteği blokladı.\n"
                        "Lütfen 2 dakika bekleyip tekrar deneyin."
                    ))
                last_error = result.get('message', 'Bilinmeyen hata')
            else:
                success_count += 1

        if success_count == len(payloads):
            self.write({
                'uts_sync_state': 'sent',
                'uts_last_response': 'Başarıyla gönderildi.',
            })
        else:
            self.write({
                'uts_sync_state': 'failed',
                'uts_last_response': last_error or 'ÜTS tarafında hata oluştu.',
            })
            raise UserError(_("ÜTS bildirimi başarısız:\n%s") % last_error)
