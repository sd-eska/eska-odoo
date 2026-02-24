import odoo
from odoo import api, SUPERUSER_ID

def fix_uts_crons(db_name):
    # Odoo configuration needs to be loaded if running standalone
    # But since we are in the workspace we can try to use the registry
    registry = odoo.registry(db_name)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Mapping old to new
        updates = {
            'model.cron_process_uts_production()': 'model.cron_uts_uretim_isleme()',
            'model.cron_process_uts_dispatch()': 'model.cron_uts_verme_isleme()',
        }
        
        for old, new in updates.items():
            actions = env['ir.actions.server'].search([('code', '=', old)])
            for action in actions:
                action.write({'code': new})
                print(f"Updated action ID {action.id}: {old} -> {new}")
        cr.commit()

if __name__ == "__main__":
    # Ensure config is loaded for standalone script
    odoo.tools.config.parse_config(['-c', 'odoo.conf'])
    fix_uts_crons('rd-odoo-uts')
