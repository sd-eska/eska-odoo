from odoo import models, fields, _
from odoo.exceptions import UserError
import logging
from datetime import datetime
from ..validators.error_codes import parse_uts_response

_logger = logging.getLogger(__name__)


class UtsSyncMixin(models.AbstractModel):
    """
    Katman 5: Gönderim Motoru (Pipeline).

    Akış: validate → build → send → parse_response → write_back
    """
    _name = 'uts.sync.mixin'
    _description = 'ÜTS Gönderim Motoru'

    uts_sync_state = fields.Selection([
        ('draft', 'Gönderilmedi'),
        ('sent', 'Gönderildi'),
        ('failed', 'Hata'),
    ], string="ÜTS Bildirim Durumu", default='draft', copy=False)

    uts_last_response = fields.Text("ÜTS Yanıtı", readonly=True, copy=False)

    # Method → Bildirim tipi eşlemesi (move.line write-back için)
    _UTS_METHOD_TO_BILDIRIMI_TIPI = {
        'uretim_bildirimi_ekle':              'uretim',
        'alim_bildirimi_ekle':                'alim',
        'verme_bildirimi_ekle':               'verme',
        'tanimsiz_yere_verme_bildirimi_ekle': 'tanimsiz_verme',
        'tuketiciye_verme_bildirimi_ekle':    'tuketici_verme',
        'kozmetik_firmaya_verme_ekle':        'kozmetik_verme',
        'ihracat_bildirimi_ekle':             'ihracat',
        'hek_zayiat_bildirimi_ekle':          'hek',
        'tuketiciden_iade_alma_ekle':         'tuketiciden_iade',
        'tanimsiz_yerden_iade_alma_ekle':     'tanimsiz_yerden_iade',
    }

    # ================================================================== #
    # Ana Pipeline
    # ================================================================== #

    def _send_to_uts(self, method_name):
        """
        Pipeline:
          1. payload üret (_prepare_uts_payloads)
          2. her payload için endpoint'e gönder
          3. yanıtı parse et (parse_uts_response)
          4. sonuca göre durum güncelle
          5. başarılıysa move.line'lara geri yaz (SNC + BID)
        """
        self.ensure_one()
        client = self.env['uts.client']
        payloads = self._prepare_uts_payloads()

        if not payloads:
            raise UserError(_(
                "ÜTS için gönderilecek geçerli veri bulunamadı.\n"
                "Ürün barkodu (UNO), tarih ve lot/seri bilgilerini kontrol edin."
            ))

        success_count = 0
        all_errors = []
        last_snc = ""
        last_bid = ""

        for payload in payloads:
            raw_result = getattr(client, method_name)(payload, self._name, self.id)

            parsed = parse_uts_response(raw_result)

            if parsed['success']:
                success_count += 1
                if parsed['snc']:
                    last_snc = parsed['snc']
                if parsed.get('bid'):
                    last_bid = parsed['bid']
            else:
                for err in parsed['errors']:
                    all_errors.append(err['translated'])
                if not parsed['errors'] and isinstance(raw_result, dict) and raw_result.get('error'):
                    all_errors.append(raw_result.get('message', 'Bilinmeyen hata'))

        # Sonuç değerlendirme
        if success_count == len(payloads):
            response_text = 'Başarıyla gönderildi.'
            if last_snc:
                response_text += f' (Kayıt No: {last_snc})'
            self.write({'uts_sync_state': 'sent', 'uts_last_response': response_text})
            self._write_back_uts_to_move_lines(method_name, last_snc, last_bid)
        else:
            error_text = '\n'.join(all_errors) if all_errors else 'Bilinmeyen hata'
            self.write({'uts_sync_state': 'failed', 'uts_last_response': error_text})
            raise UserError(_("ÜTS bildirimi başarısız:\n%s") % error_text)

    # ================================================================== #
    # Move Line Write-Back (SNC + BID)
    # ================================================================== #

    def _write_back_uts_to_move_lines(self, method_name, snc, bid=''):
        """Başarılı gönderim sonrası move.line'lara ÜTS meta verisini yazar."""
        bildirimi_tipi = self._UTS_METHOD_TO_BILDIRIMI_TIPI.get(method_name)
        if not bildirimi_tipi:
            return

        vals = {
            'uts_bildirimi_tipi': bildirimi_tipi,
            'uts_gonderildi': True,
            'uts_kayit_tarihi': datetime.now(),
        }
        if snc:
            vals['uts_kayit_no'] = str(snc)
        if bid:
            vals['uts_bildirim_kodu'] = str(bid)

        move_lines = self._get_related_move_lines()
        if move_lines:
            move_lines.write(vals)
            _logger.info(
                "ÜTS write-back: %d move.line güncellendi (tip=%s, snc=%s, bid=%s)",
                len(move_lines), bildirimi_tipi, snc, bid
            )

    def _get_related_move_lines(self):
        """Model tipine göre ilgili move.line kayıtlarını bulur."""
        if self._name == 'stock.picking':
            return self.move_line_ids.filtered(
                lambda l: l.product_id.is_uts_tracked
            )
        elif self._name == 'mrp.production':
            return self.move_finished_ids.mapped('move_line_ids').filtered(
                lambda l: l.product_id == self.product_id
            )
        elif self._name == 'stock.scrap':
            if self.move_id:
                return self.move_id.move_line_ids
        return self.env['stock.move.line']
