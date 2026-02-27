from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class UtsLog(models.Model):
    """ÜTS bildirim kayıtları. Her API isteği için bir satır oluşur."""
    _name = 'uts.log'
    _description = 'ÜTS Bildirim Logu'
    _order = 'create_date desc'

    name = fields.Char("İşlem Tipi")
    res_model = fields.Char("Model")
    res_id = fields.Integer("Kayıt ID")
    request_data = fields.Text("İstek Verisi")
    response_data = fields.Text("Yanıt Verisi")
    status_code = fields.Integer("Durum Kodu")
    summary = fields.Text("Özet", compute="_compute_summary", store=True)
    state = fields.Selection([
        ('success', 'Başarılı'),
        ('failed', 'Hata'),
    ], string="Durum", compute="_compute_state", store=True)

    @api.depends('status_code', 'response_data')
    def _compute_summary(self):
        for rec in self:
            if rec.status_code == 200:
                rec.summary = "Başarılı"
            elif rec.status_code == 403:
                rec.summary = "Bakanlık Güvenlik Duvarı Engeli"
            elif rec.status_code == 0:
                rec.summary = "Bağlantı Hatası"
            elif "Request Rejected" in (rec.response_data or ""):
                rec.summary = "Sunucu tarafından bloklandı."
            else:
                rec.summary = f"ÜTS hata döndürdü (Kod: {rec.status_code})."

    @api.depends('status_code')
    def _compute_state(self):
        for rec in self:
            rec.state = 'success' if rec.status_code == 200 else 'failed'

    @api.model
    def _cron_cleanup_old_logs(self):
        """
        30 günden eski BAŞARILI logları siler.
        Hata logları (state='failed') sonsuza dek saklanır.
        Haftalık cron ile çalışır.
        """
        cutoff = fields.Datetime.now() - relativedelta(days=30)
        old_success_logs = self.search([
            ('state', '=', 'success'),
            ('create_date', '<', cutoff),
        ])
        count = len(old_success_logs)
        old_success_logs.unlink()
        if count:
            import logging
            logging.getLogger(__name__).info(
                "ÜTS Log Temizleme: %d başarılı kayıt silindi (30 günden eski).", count
            )
