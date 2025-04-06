
from odoo import models, fields , api

class DailyReports(models.Model):
    _name = "daily_reports"
    _description = 'Daily Reports'

    partner_id = fields.Many2one(
        'res.partner',  # الربط مع جهات الاتصال
        string="العميل",
        required=True  # يمكن جعله إلزاميًا أو لا حسب الحاجة
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="المسؤول",
        default=lambda self: self.env.user,
        required=True
    )

    team_id = fields.Many2one(
        'crm.team',
        string="Sales Team"
    )

    '''shop_owner_name = fields.Char()
    shop_supervisor = fields.Char()'''
    team = fields.Char()
    time_of_visit = fields.Datetime()
    end_of_date_visit = fields.Datetime()
    district = fields.Char(related='partner_id.city',readonly='1')
    state_g = fields.Char(related='partner_id.state_id.name',readonly='1',string="المحافظة")
    area = fields.Char(related='partner_id.street2')
    street = fields.Char(related='partner_id.street')
    battery_okaya = fields.Boolean()
    okaya_inverter = fields.Boolean()
    hyperd_inverter= fields.Boolean()
    mppt_controller = fields.Boolean()
    solar_panel = fields.Boolean()
    lithium_battery = fields.Boolean()
    daya_inverter= fields.Boolean()
    distilled_water = fields.Boolean()
    another = fields.Text()
    account_statement = fields.Boolean()
    debt_report = fields.Boolean()
    preview_battery_production_date = fields.Date()
    preview_inverter_production_date = fields.Date()
    compliance_sales_policy = fields.Boolean()
    reason = fields.Text()
    product_price_list = fields.Boolean()
    total_debt = fields.Integer()
    number_of_warranty_cards= fields.Integer()
    number_of_maintenance_requests = fields.Integer()
    type_of_maintenance_requests= fields.Text()
    battery_okaya_delivery = fields.Char()
    inverter_okaya_delivery = fields.Char()
    hyperd_inverter_delivery = fields.Char()
    mppt_controller_delivery = fields.Char()
    solar_panel_delivery = fields.Char()
    lithium_battery_delivery = fields.Char()
    daya_inverter_delivery = fields.Char()
    distilled_water_delivery = fields.Char()
    another_delivery = fields.Text()
    new_warranty_cards_delivery = fields.Boolean()
    delivery_battery_instructions_guidelines = fields.Boolean()
    cash = fields.Integer()
    credit = fields.Integer()
    collection = fields.Integer()
    other_notes = fields.Text()

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
    def create(self, vals):
        res = super(DailyReports, self).create(vals)
        print("inner the create method")
        return res


    @api.model
    def web_read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        print("web_read_group is being executed!")
        print("Domain:", domain)
        print("Fields:", fields)
        print("Group By:", groupby)

        return super(DailyReports, self).web_read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)



    def write(self, vals):
        if 'state' in vals and not self.env.user.has_group('distributor_track.distributor_manager_group'):
            raise models.ValidationError("ليس لديك الصلاحيات لتغيير حالة التقرير.")

        res = super(DailyReports, self).write(vals)
        print("inner write method")
        return res

    def unlink(self):
        res = super(DailyReports, self).unlink()
        print("inner the delete method")
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
            record.state = '1_done'  # تغيير إلى 'reviewed' بدلاً من 'done'
            record.reviewed_by = self.env.user