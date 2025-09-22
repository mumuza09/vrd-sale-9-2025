# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Tracking GPS',
    'version': '18.0.1.0.0',
    'sequence': 1,
    'category': 'Authen',
    'description':
        """
This Module help to Tracking GPS

    """,
    'summary': 'This Module help to create Tracking GPS',
    'depends': ['base','web'],
    'assets': {
        'web.assets_frontend': [
            'tracking_gps/static/src/js/custom_script_fe.js',
        ],
        'web.assets_backend': [
            'tracking_gps/static/src/js/custom_script_be.js',
            'tracking_gps/static/src/js/tracking_map.js',
            'tracking_gps/static/src/xml/tracking_user_view.xml',
            'tracking_gps/static/src/css/style.scss'
        ],
        'web.assets_qweb': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/osm_map_template.xml',
        'views/osm_map_menu.xml',
        'data/scheduled_action.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['static/description/icon.png', 'images/main_screenshot.gif','static/description/map.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':100.0,
    'currency':'THB',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'pre_init_hook' :'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
