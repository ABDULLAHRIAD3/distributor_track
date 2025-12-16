from datetime import timedelta
from odoo import models, fields, api


class DailyVisitSummary(models.Model):
    _name = 'daily.visit.summary'
    _description = 'Daily Visit Summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Report Name", default="ملخص الزيارات اليومية لتاريخ ", required=True,tracking=1)
    user_id = fields.Many2one('res.users',
                            string="Sales Representative",
                            required=True,
                            default=lambda self: self.env.user,
                            readonly=True,
    )
    assistant_id = fields.Many2one(
        'res.users',
        string="Assistant Sales Representative",
        help="اختر مساعد المندوب من قائمة الموظفين"
    )

    date = fields.Date(string="Date", required=True, tracking=1)
    company_id = fields.Many2one(
        'res.company',
        string="Parent Company",
        required=True,
        default=lambda self: self.env.company,
        tracking=1,
        help="اختر الشركة الأم المرتبطة بالشركة الفرعية"
    )

    child_company_id = fields.Many2one(
        'res.company',
        string="Branch/Child Company",
        tracking=1,
        help="اختر الشركة الفرعية المرتبطة بالشركة الأم"
    )

    allowed_child_company_ids = fields.Many2many(
        'res.company',
        compute='_compute_allowed_child_companies',
        string="Allowed Child Companies"
    )

    status = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed')],
        string="Status",
        default='draft',
        tracking=1
    )
    distributor = fields.Many2one('res.partner', string="Distributor", tracking=1)
    cash = fields.Integer(string="Cash")
    deferred_payment = fields.Integer(string="Deferred Payment", compute="_compute_totals", store=True)
    collection = fields.Integer(string="Collection")
    notes = fields.Text(string="Notes")
    total_visits = fields.Integer(string="Number of Visits", compute="_compute_totals", store=True)
    total_cash = fields.Integer(string="Total Cash", compute="_compute_totals", store=True)
    total_credit = fields.Integer(string="Total Deferred Payment", compute="_compute_totals", store=True)
    total_collection = fields.Integer(string="Total Collection", compute="_compute_totals", store=True)
    percent_vs_prev_day = fields.Float(string="Percent vs Prev Day", compute="_compute_totals", digits=(12, 2))
    percent_vs_7day_avg = fields.Float(string="Percent vs 7-day Avg", compute="_compute_totals", digits=(12, 2))
    first_time_customers = fields.Integer(string="First-time Customers", compute="_compute_totals", store=True)

    visit_report_ids = fields.One2many(
        'daily.visit.summary.line', 'summary_id', string="Visit Reports"
    )
    show_draft_button = fields.Boolean(compute='_compute_show_buttons')
    show_confirmed_button = fields.Boolean(compute='_compute_show_buttons')

    @api.depends('status')
    def _compute_show_buttons(self):
        for rec in self:
            rec.show_draft_button = rec.status in ('confirmed')
            rec.show_confirmed_button = rec.status in ('draft')
    
    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for rec in records:
            rec.message_post(body=f"تم إنشاء الملخص لليوم {rec.date}")
        return records

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec.message_post(body="تم تحديث الملخص اليومي")
        return res
    
    def unlink(self):
        for rec in self:
            rec.message_post(body="تم حذف التقرير")
        return super().unlink()
    
    def action_draft(self):
        for res in self:
            res.status = 'draft'

    def action_confirm(self):
        for res in self:
            res.status = 'confirmed'

    @api.onchange('date', 'user_id')
    def _onchange_load_visits(self):
        if self.date and self.user_id:
            start = fields.Datetime.to_datetime(self.date)
            end = start + timedelta(days=1) - timedelta(seconds=1)

            reports = self.env['daily_reports'].search([
                ('user_id', '=', self.user_id.id),
                ('time_of_visit', '>=', start),
                ('time_of_visit', '<=', end),
            ])

            self.visit_report_ids = [(5, 0, 0)]
            self.visit_report_ids = [(0, 0, {
                'distributor': r.partner_id.name,
                'cash': r.cash,
                'credit': r.credit,
                'collection': r.collection,
                'notes': r.other_notes,
                'time_of_visit': r.time_of_visit,
            }) for r in reports]

    @api.model
    def get_chart_data(self, ids):
        record = self.browse(ids[0])
        visits_today = record.visit_report_ids
        total_cash = sum(v.cash for v in visits_today)
        total_collection = sum(v.collection for v in visits_today)
        total_credit = sum(v.credit for v in visits_today)

        visits_labels = [v.distributor.name if v.distributor else 'Unknown' for v in visits_today]
        visits_cash = [v.cash for v in visits_today]
        visits_credit = [v.credit for v in visits_today]

        daily_labels = []
        daily_collection = []
        for i in range(7, 0, -1):
            day = record.date - timedelta(days=i)
            daily_labels.append(day.strftime('%Y-%m-%d'))
            day_reports = self.env['daily_reports'].search([
                ('user_id', '=', record.user_id.id),
                ('time_of_visit', '>=', day.strftime('%Y-%m-%d 00:00:00')),
                ('time_of_visit', '<=', day.strftime('%Y-%m-%d 23:59:59')),
            ])
            daily_collection.append(sum(r.collection for r in day_reports))

        return {
            'total_cash': total_cash,
            'total_collection': total_collection,
            'total_credit': total_credit,
            'visits_labels': visits_labels,
            'visits_cash': visits_cash,
            'visits_credit': visits_credit,
            'daily_labels': daily_labels,
            'daily_collection': daily_collection,
        }

    @api.depends('visit_report_ids.time_of_visit', 'user_id', 'visit_report_ids.collection', 'visit_report_ids.credit')
    def _compute_totals(self):
        for rec in self:
            # default values
            rec.total_visits = 0
            rec.total_collection = 0.0
            rec.total_credit = 0.0
            rec.total_cash = 0.0
            rec.percent_vs_prev_day = 0.0
            rec.percent_vs_7day_avg = 0.0
            rec.first_time_customers = 0

            if not (rec.date and rec.user_id):
                continue

            # prepare date range
            start_dt = fields.Datetime.to_string(rec.date)
            end_dt = fields.Datetime.to_string(rec.date + timedelta(days=1) - timedelta(seconds=1))

            domain_today = [
                ('user_id', '=', rec.user_id.id),
                ('time_of_visit', '>=', start_dt),
                ('time_of_visit', '<=', end_dt),
            ]

            # total visits
            rec.total_visits = self.env['daily_reports'].search_count(domain_today)

            # sum totals
            reports_today = self.env['daily_reports'].search(domain_today)
            rec.total_cash = sum(r.cash for r in reports_today)
            rec.total_collection = sum(r.collection for r in reports_today)
            rec.total_credit = sum(r.credit for r in reports_today)

            # percent vs previous day
            prev_start = fields.Datetime.to_string(rec.date - timedelta(days=1))
            prev_end = fields.Datetime.to_string(rec.date - timedelta(days=1) + timedelta(days=1) - timedelta(seconds=1))
            domain_prev = [
                ('user_id', '=', rec.user_id.id),
                ('time_of_visit', '>=', prev_start),
                ('time_of_visit', '<=', prev_end),
            ]
            prev_total = sum(r.collection for r in self.env['daily_reports'].search(domain_prev))
            if prev_total:
                rec.percent_vs_prev_day = ((rec.total_collection - prev_total) / prev_total) * 100.0
            else:
                rec.percent_vs_prev_day = 100.0 if rec.total_collection > 0 else 0.0

            # percent vs 7-day avg (excluding current day)
            start_7 = rec.date - timedelta(days=7)
            domain_7 = [
                ('user_id', '=', rec.user_id.id),
                ('time_of_visit', '>=', fields.Datetime.to_string(start_7)),
                ('time_of_visit', '<', start_dt),
            ]
            sum_7 = sum(r.collection for r in self.env['daily_reports'].search(domain_7))
            avg_7 = sum_7 / 7.0
            if avg_7:
                rec.percent_vs_7day_avg = ((rec.total_collection - avg_7) / avg_7) * 100.0
            else:
                rec.percent_vs_7day_avg = 100.0 if rec.total_collection > 0 else 0.0

            # first-time customers
            partners = reports_today.mapped('partner_id')
            first_time_count = 0
            for partner in partners:
                prior_count = self.env['daily_reports'].search_count([
                    ('partner_id', '=', partner.id),
                    ('time_of_visit', '<', start_dt),
                ])
                if prior_count == 0:
                    first_time_count += 1
            rec.first_time_customers = first_time_count


    @api.depends('company_id')
    def _compute_allowed_child_companies(self):
        for rec in self:
            if rec.company_id:
                # جلب الشركات الفرعية المباشرة + الشركة نفسها
                child_companies = self.env['res.company'].search([
                    '|',
                    ('parent_id', '=', rec.company_id.id),
                    ('id', '=', rec.company_id.id)
                ])
                rec.allowed_child_company_ids = child_companies
            else:
                rec.allowed_child_company_ids = False

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.child_company_id = False
        if self.company_id:
            return {
                'domain': {
                    'child_company_id': [
                        '|',
                        ('parent_id', '=', self.company_id.id),
                        ('id', '=', self.company_id.id)
                    ]
                }
            }
        # تصدير التقرير PDF
    def action_export_pdf(self):
        return self.env.ref('distributor_track.action_daily_visit_summary_pdf').report_action(self)

