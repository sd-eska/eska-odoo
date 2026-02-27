from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    uts_bildirimi_tipi = fields.Selection([
        ('uretim', 'Üretim'),
        ('alim', 'Alım'),
        ('verme', 'Verme'),
        ('tanimsiz_verme', 'Tanımsız Yere Verme'),
        ('tuketici_verme', 'Tüketici Verme'),
        ('kozmetik_verme', 'Kozmetik Verme'),
        ('ihracat', 'İhracat'),
        ('hek', 'HEK/Zayiat'),
        ('tuketiciden_iade', 'Tüketiciden İade'),
        ('tanimsiz_yerden_iade', 'Tanımsız Yerden İade'),
    ], string="ÜTS Bildirim Tipi", readonly=True, copy=False)

    uts_kayit_no = fields.Char(
        string="ÜTS Kayıt No",
        readonly=True, copy=False,
        help="ÜTS'den dönen SNC (Kayıt Numarası)"
    )

    uts_bildirim_kodu = fields.Char(
        string="ÜTS Bildirim Kodu",
        readonly=True, copy=False,
        help="ÜTS'den dönen BID — iptal ve iade işlemlerinde referans olarak kullanılır."
    )

    uts_kayit_tarihi = fields.Datetime(
        string="ÜTS Kayıt Tarihi",
        readonly=True, copy=False
    )

    uts_gonderildi = fields.Boolean(
        string="ÜTS'ye Gönderildi",
        default=False, readonly=True, copy=False
    )
