from odoo import models, fields , api
from odoo.exceptions import ValidationError


class DailyReports(models.Model):
    _name = "daily_reports"
    _description = 'Daily Reports'
    _inherit = ["mail.thread.main.attachment", "mail.activity.mixin"]

    partner_id = fields.Many2one(
        'res.partner',  # الربط مع جهات الاتصال
        string="العميل",
        required=True  # يمكن جعله إلزاميًا أو لا حسب الحاجة
    )

    #date_of_oldest_battary = fields.One2many(
     #   comodel_name='res.partner',
      #  string="f"
    #)
    date_of_oldest_battery = fields.Date(string="تاريخ أقدم بطارية", readonly=False, tracking=1,required=True)

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="المسؤول",
        default=lambda self: self.env.user,
        required=True
    )

    team_id = fields.Many2one(
        'crm.team',
        string="Sales Team",
        required=True
    )

    '''shop_owner_name = fields.Char()
    shop_supervisor = fields.Char()'''
    team = fields.Char(tracking=1)
    time_of_visit = fields.Datetime(required=True,tracking=1)
    end_of_date_visit = fields.Datetime(required=True,tracking=1)
    district = fields.Char(related='partner_id.city',readonly='1',tracking=1)
    state_g = fields.Char(related='partner_id.state_id.name',readonly='1',string="المحافظة",tracking=1)
    area = fields.Char(related='partner_id.street2',tracking=1)
    street = fields.Char(related='partner_id.street',tracking=1)
    battery_okaya = fields.Boolean(tracking=1)
    okaya_inverter = fields.Boolean(tracking=1)
    hyperd_inverter= fields.Boolean(tracking=1)
    mppt_controller = fields.Boolean(tracking=1)
    solar_panel = fields.Boolean(tracking=1)
    lithium_battery = fields.Boolean(tracking=1)
    daya_inverter= fields.Boolean(tracking=1)
    distilled_water = fields.Boolean(tracking=1)
    another = fields.Text(tracking=1)
    account_statement = fields.Boolean(tracking=1)
    debt_report = fields.Boolean(tracking=1)
    preview_battery_production_date = fields.Date(tracking=1)
    compliance_sales_policy = fields.Boolean(tracking=1)
    reason = fields.Text(tracking=1)
    product_price_list = fields.Boolean(tracking=1)
    total_debt = fields.Float(tracking=1)
    number_of_warranty_cards= fields.Integer(tracking=1)
    number_of_maintenance_requests = fields.Integer(tracking=1)
    type_of_maintenance_requests= fields.Text(tracking=1)
    battery_okaya_delivery = fields.Char(tracking=1)
    inverter_okaya_delivery = fields.Char(tracking=1)
    hyperd_inverter_delivery = fields.Char(tracking=1)
    mppt_controller_delivery = fields.Char(tracking=1)
    solar_panel_delivery = fields.Char(tracking=1)
    lithium_battery_delivery = fields.Char(tracking=1)
    daya_inverter_delivery = fields.Char(tracking=1)
    distilled_water_delivery = fields.Char(tracking=1)
    another_delivery = fields.Text(tracking=1)
    new_warranty_cards_delivery = fields.Boolean(tracking=1)
    delivery_battery_instructions_guidelines = fields.Boolean(tracking=1)
    cash = fields.Float(tracking=1)
    credit = fields.Float(tracking=1)
    collection = fields.Float(tracking=1)
    other_notes = fields.Text(tracking=1)
    circuit_breakers = fields.Boolean(tracking=1)
    electrical_cables = fields.Boolean(tracking=1)
    electrical_cables_delivery = fields.Char(tracking=1)
    circuit_breakers_delivery = fields.Char(tracking=1)

    state = fields.Selection([
        ('draft', 'بإنتظار المراجعه'),
        ('in_progress', 'قيد المراجعة'),
        ('1_done', 'تمت مراجعته'),
    ], string="الحالة", default='draft', tracking=True)

    reviewed_by = fields.Many2one('res.users', string="مراجع من قبل")

    @api.model
    def _expand_states(self, states, domain, order=None):
        return ['draft', 'in_progress', 'done', 'reviewed']

    @api.model_create_multi
    @api.model
    def create(self, vals):
        report = super(DailyReports, self).create(vals)
        if vals.get('partner_id') and vals.get('date_of_oldest_battery'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            partner.date_of_oldest_battery = vals['date_of_oldest_battery']
        return report

    @api.model
    def web_read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        return super(DailyReports, self).web_read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.date_of_oldest_battery = self.partner_id.date_of_oldest_battery
        else:
            self.date_of_oldest_battery = False

    @api.constrains('time_of_visit', 'end_of_date_visit')
    def _check_visit_dates(self):
        for rec in self:
            if rec.end_of_date_visit and rec.time_of_visit and rec.end_of_date_visit < rec.time_of_visit:
                raise ValidationError("تاريخ نهاية الزيارة لا يمكن أن يكون قبل بدايتها.")

    def write(self, vals):
        res = super(DailyReports, self).write(vals)
        for rec in self:
            if vals.get('date_of_oldest_battery') and rec.partner_id:
                rec.partner_id.date_of_oldest_battery = vals['date_of_oldest_battery']
        if 'state' in vals and not self.env.user.has_group('distributor_track.distributor_manager_group'):
            raise models.ValidationError("ليس لديك الصلاحيات لتغيير حالة التقرير.")
        return res

    def unlink(self):
        res = super(DailyReports, self).unlink()
        return res

    def action_draft(self):
        for res in self:
            res.state = 'draft'

    def action_in_progress(self):
        for res in self:
            res.state = 'in_progress'

    def action_done(self):
        for res in self:
            res.state = '1_done'

    def action_mark_reviewed(self):
        """يتم تعيين التقرير كمراجع ومكتمل"""
        for record in self:
            record.state = '1_done'  #
            record.reviewed_by = self.env.user