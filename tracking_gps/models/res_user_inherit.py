from odoo import models, fields

class PartnerLocation(models.Model):
    _name = 'partner.location'
    _description = 'Partner Locations'
    
    partner_id = fields.Many2one('res.partner', string="Partner", required=True, ondelete='cascade')
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")
    date = fields.Datetime(string="Date")

class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'

    location_ids = fields.One2many('partner.location', 'partner_id', string="Locations")
