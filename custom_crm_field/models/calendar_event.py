from odoo import models, fields, api

class CalendarEvent(models.Model):
    _inherit = "calendar.event"
    res_model_name = fields.Char(related='res_model_id.name')

    @api.depends('res_model_id', 'res_id')
    def _compute_crm_data(self):
        for rec in self:
            rec.crm_contact_name = False
            rec.crm_phone = False
            rec.crm_note = False
            model = rec.sudo().res_model_id.model

            if model == 'crm.lead' and rec.res_id:
                lead = self.env['crm.lead'].sudo().browse(rec.res_id)
                if lead.exists():
                    rec.crm_contact_name = lead.x_studio_contact_name
                    rec.crm_phone = lead.phone
                    rec.crm_note = lead.description

    crm_contact_name = fields.Char(string="Contact Name", compute='_compute_crm_data')
    crm_phone = fields.Char(string="Phone", compute='_compute_crm_data')
    crm_note = fields.Html(string="Note", compute='_compute_crm_data')
