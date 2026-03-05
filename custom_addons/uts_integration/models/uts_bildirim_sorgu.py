from odoo import models, fields, _, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class UtsBildirimSorguLine(models.TransientModel):
    """Bildirim Sorgula sonuç satırı."""
    _name = 'uts.bildirim.sorgu.line'
    _description = 'ÜTS Bildirim Sorgu Sonucu'

    wizard_id = fields.Many2one('uts.bildirim.sorgu', ondelete='cascade')
    bildirim_tipi = fields.Char("Bildirim Tipi")
    bildirim_kodu = fields.Char("Bildirim Kodu (BID)")
    bildirim_durumu = fields.Char("Durum")
    bildirim_zamani = fields.Char("Bildirim Zamanı")
    uno = fields.Char("UNO")
    lno = fields.Char("LNO")
    sno = fields.Char("SNO")
    adt = fields.Integer("Adet")
    bno = fields.Char("Belge No")
    kun = fields.Char("Kurum No")
    git = fields.Char("İşlem Tarihi")


class UtsBildirimSorgu(models.TransientModel):
    """
    ÜTS Bildirim Sorgula Wizard'ı (3.4.9).
    Kullanıcı UNO/LNO/SNO girer, ÜTS API'ye sorgu gönderir,
    sonuçları tree view'da gösterir.
    """
    _name = 'uts.bildirim.sorgu'
    _description = 'ÜTS Bildirim Sorgula'

    uno = fields.Char("Ürün Numarası (UNO)", size=23)
    lno = fields.Char("Lot/Batch Numarası (LNO)", size=36)
    sno = fields.Char("Seri/Sıra Numarası (SNO)", size=36)
    kayit_sayisi = fields.Integer("Kayıt Sayısı", default=10, help="En fazla kaç kayıt getirilsin?")
    offset = fields.Char("Sonraki Sayfa (OFF)", readonly=True)
    sonuc_ids = fields.One2many('uts.bildirim.sorgu.line', 'wizard_id', string="Sonuçlar")

    def action_sorgula(self):
        """ÜTS API'ye bildirim sorgulama isteği gönderir."""
        self.ensure_one()
        client = self.env['uts.client']

        vals = {}
        if self.uno:
            vals['UNO'] = self.uno.strip()
        if self.lno:
            vals['LNO'] = self.lno.strip()
        if self.sno:
            vals['SNO'] = self.sno.strip()
        vals['ADT'] = max(1, min(500, self.kayit_sayisi or 10))

        if self.offset:
            vals['OFF'] = self.offset

        raw_result = client.bildirim_sorgula(vals)

        # Sonuçları parse et
        lines_data = []
        off = None

        if isinstance(raw_result, dict):
            snc = raw_result.get('SNC', {})

            if isinstance(snc, dict):
                # offset parametreli endpoint → SNC.LST + SNC.OFF
                lst = snc.get('LST', [])
                off = snc.get('OFF')
            elif isinstance(snc, list):
                # basit endpoint → SNC doğrudan liste
                lst = snc
            else:
                lst = []

            for item in (lst or []):
                if not isinstance(item, dict):
                    continue
                lines_data.append((0, 0, {
                    'bildirim_tipi': item.get('BTI', ''),
                    'bildirim_kodu': item.get('BID', ''),
                    'bildirim_durumu': item.get('BDR', ''),
                    'bildirim_zamani': item.get('BZA', ''),
                    'uno': item.get('UNO', ''),
                    'lno': item.get('LNO', ''),
                    'sno': item.get('SNO', ''),
                    'adt': item.get('ADT', 0),
                    'bno': item.get('BNO', ''),
                    'kun': str(item.get('KUN', '')),
                    'git': item.get('GIT', ''),
                }))

            # Hata kontrol
            msj = raw_result.get('MSJ', [])
            if isinstance(msj, list):
                for msg in msj:
                    if isinstance(msg, dict) and msg.get('TIP') == 'HATA':
                        raise UserError(_("[%s] %s") % (msg.get('KOD', ''), msg.get('MET', '')))

        self.write({
            'sonuc_ids': [(5, 0, 0)] + lines_data,
            'offset': off or '',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'uts.bildirim.sorgu',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_sonraki_sayfa(self):
        """Sonraki sayfa sonuçlarını yükler."""
        if not self.offset:
            raise UserError(_("Sonraki sayfa mevcut değil."))
        return self.action_sorgula()
