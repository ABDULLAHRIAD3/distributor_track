# -*- coding: utf-8 -*-
# Copyright 2025 Abdullah Riad
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

{
    'name': "Distributor Track",
    'summary': "Daily visit tracking, KPIs, dashboards, distributors performance",
    'description': "Module for tracking sales representatives’ daily visits, KPIs, charts, and summaries.",
    'author': "Abdullah Riad",
    'version': '18.0.1.0',
    'category': 'Sales',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'contacts',
        'crm',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/daily_reports_view.xml',
        'views/res_partner_view.xml',
        'views/daily_visit_summary_views.xml',
        'data/paperformat.xml',
        'report/daily_visit_summary_report.xml',
    ],

    'assets': {
        'web.report_assets_common': [
            'distributor_track/static/src/css/daily_report_template.css',
        ],
        'web.assets_backend': [
            'distributor_track/static/src/css/dashboard.css',
            'distributor_track/static/src/js/package.json',
        ],
    },

    'installable': True,
    'application': True,
}
