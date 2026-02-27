"""
Kozmetik Firmaya Verme Bildirimi (3.1.5) payload üretim mantığı.
Pure Python mixin — Odoo model değil.
"""
import logging
import datetime

_logger = logging.getLogger(__name__)


class KozmetikBuilderMixin:

    def _build_kozmetik_verme_payloads_from_picking(self, picking):
        """
        Kozmetik firmaya verme bildirimi payload listesi.
        Zorunlu: UNO, LNO/SNO, ADT (lot), KUN, BNO
        Opsiyonel: GIT (varsayılan = bugün)
        """
        from odoo import _
        from odoo.exceptions import UserError

        partner = picking.partner_id
        KUN = partner.uts_institution_no or partner.commercial_partner_id.uts_institution_no
        if not KUN:
            raise UserError(_(
                "Kozmetik Firmaya Verme: Müşterinin KUN numarası eksik.\n"
                "Lütfen müşteri kartından 'ÜTS Kurum Numarası' alanını doldurun."
            ))

        git_date = picking.date_done or datetime.date.today()
        if hasattr(git_date, 'date'):
            git_date = git_date.date()
        GIT = git_date.strftime('%Y-%m-%d')

        payloads = []
        for move, line, data in self._iter_verme_lines(picking, "Kozmetik Verme"):
            self._require_lot_for_verme(data, move.product_id.name, "Kozmetik Verme")

            payload = {
                'UNO': data['uno'],
                'KUN': KUN,
                'BNO': picking.name,
                'GIT': GIT,
            }
            self._apply_tracking(payload, data['tracking'], data['lot'], data['qty'])
            payloads.append(payload)

        return payloads
