from odoo import models, fields

class CRMStage(models.Model):
    _inherit = "crm.stage"

    company_id = fields.Many2one("res.company", string="Company", required=True, default=lambda self: self.env.company)
