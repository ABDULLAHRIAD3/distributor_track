from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    date_of_oldest_battery = fields.Date()