{
    'name': 'CRM-Lead-CustomField',
    'version': '1.0',
    'summary': '',
    'sequence': 10,
    'description': "",
    'category': 'Sales',
    'website': '',
    'depends': ['crm'],
    'data': [
        'views/crm_pipeline_view.xml',
        'views/crm_page_view.xml',
        'views/crm_stage_view.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/calendar_event_inherit.xml'
    ],
    'installable': True,
    'application': True
}