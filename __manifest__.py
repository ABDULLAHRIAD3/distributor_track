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
    'assets':{
        'web.assets_backend':[
            'distributor_track\static\src\css\distributor_track.css'
        ]
    },
    'installable': True,
    'application': True,
}