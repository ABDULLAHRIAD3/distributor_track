# -*- coding: utf-8 -*-
# Copyright 2025 Abdullah Riad Joher <abdullah22riad@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    date_of_oldest_battery = fields.Date()