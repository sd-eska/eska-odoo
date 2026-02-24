import odoo
from odoo import api, SUPERUSER_ID

conf = odoo.tools.config
conf.parse_config(['-c', 'odoo.conf'])
odoo.cli.shell.Shell.init_odoo(conf)

db_name = conf['db_name']
registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Create default type if missing
    types = env['estate.property.type'].search([], limit=1)
    if not types:
        types = env['estate.property.type'].create({'name': 'Apartment'})
    
    # Fix properties
    recs = env['estate.property'].search([])
    for r in recs:
        if r.expected_price <= 0:
            r.expected_price = 1.0
        if not r.property_type_id:
            r.property_type_id = types.id
    
    # Fix offers
    offers = env['estate.property.offer'].search([('price', '<=', 0)])
    for o in offers:
        o.price = 1.0
        
    cr.commit()
