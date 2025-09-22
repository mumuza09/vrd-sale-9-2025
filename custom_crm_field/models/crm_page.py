from odoo import models, fields

class CRMPage(models.Model):
    _name = 'crm.page'
    _description = 'CRM Page'

    name = fields.Char(string="Name", required=True)
