import json
import logging
import psycopg2
import requests


import odoo
import odoo.modules.registry
from odoo import http, fields
from odoo.http import request
from odoo.addons.web.controllers.home import Home 
from datetime import datetime, timedelta
import json
import secrets
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url, is_user_internal
from odoo.exceptions import AccessError
from odoo.service import security

_logger = logging.getLogger(__name__)

class CustomLoginController(Home):

    def _response(self, status, code, message, data=None, errors=None):
        """
        Utility function to standardize API responses
        """
        response = {
            "status": status,
            "code": code,
            "message": message,
        }
        if data is not None:
            response["data"] = data
        if errors is not None:
            response["errors"] = errors
        return http.Response(
            json.dumps(response), content_type="application/json", status=code
        )

    @http.route('/save-location', type='json', auth='user', methods=['POST'])
    def save_location(self, **kwargs):
        user = request.env.user  # Get the currently logged-in user
        partner = user.partner_id  # Get the user's associated partner record

        # Extract latitude and longitude from the request
        # latitude = kwargs.get('latitude')
        # longitude = kwargs.get('longitude')
        # _logger.info(f"kwargs {kwargs}")

        json_data = json.loads(request.httprequest.data)
        latitude = json_data["latitude"]
        longitude = json_data["longitude"]

        _logger.info(f"json_data {json_data}")        

        _logger.info(f"latitude [{latitude}] longitude [{longitude}]")
        
        if latitude and longitude:
            # Create a new partner.location record
            location = request.env['partner.location'].sudo().create({
                'partner_id': user.partner_id.id,  # Link to the current user's partner
                'latitude': latitude,
                'longitude': longitude,
            })
            return {'status': 'success', 'message': 'Location saved', 'location_id': location.id}
        else:
            return {'status': 'error', 'message': 'Latitude and Longitude are required'}    
    
    @http.route('/osm-map', type='http', auth='public', website=True)
    def osm_map(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        return request.render('tracking_gps.osm_map_page',{
            'lat': lat,
            'lon': lon,
        })
    
    @http.route('/get-locations', type='json', auth='public', methods=['POST'])
    def get_locations(self):

        json_data = json.loads(request.httprequest.data)
        counts = json_data["counts"]

        _logger.info(f"json_data {json_data}")

        locations = request.env['partner.location'].sudo().search([])
        data = [{'name': loc.partner_id.name, 'latitude': loc.latitude, 'longitude': loc.longitude} for loc in locations]
        return data

    