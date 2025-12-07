from odoo import models, fields


class DailyVisitSummaryLine(models.Model):
    _name = 'daily.visit.summary.line'
    _description = 'Daily Visit Summary Line'

    summary_id = fields.Many2one('daily.visit.summary', string="Daily Summary")
    distributor = fields.Char(string="Distributor")
    cash = fields.Integer(string="Cash")
    credit = fields.Integer(string="Deferred Payment")
    collection = fields.Integer(string="Collection")
    notes = fields.Text(string="Notes")
    time_of_visit = fields.Datetime(string="Visit Time")
