# -*- coding: utf-8 -*-
# Copyright 2025 Abdullah Riad Joher <abdullah22riad@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)
{
    'name': "Distributor Track",
    'author': "Abdullah Riad",
    'category': '',
    'version': '18.0.1.0',
    'depends': ['base','contacts','crm',
                ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/daily_reports_view.xml',
        'views/res_partner_view.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}