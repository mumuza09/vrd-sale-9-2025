from odoo import models, fields, api
from datetime import datetime, time
import logging
import requests

_logger = logging.getLogger(__name__)

class ScheduleLine(models.Model):
    _name = 'schedule.line'
    _description = 'Schedule lineOA'

    name = fields.Char(string="Name")

    def scheduled_function(self):
        """Function to be called every day at 09:15, except on Sunday."""
        now = datetime.now()
        weekday = now.weekday()  # 0 = Monday, 6 = Sunday

        # Check if today Sunday (6)
        if weekday == 6:
            _logger.info("Function skipped, today is weekend (Saturday or Sunday).")
            return
        
        # Your custom logic here
        _logger.info(f"Function called at: {now}")


        # Define today's date
        today = fields.Date.today()
        
        # Define the time range (9:00 AM - 9:15 AM)
        start_time = datetime.combine(today, time(9, 0, 0))
        end_time = datetime.combine(today, time(9, 15, 0))

        # Query partner.location records within this time range
        locations = self.env['partner.location'].search([
            ('create_date', '>=', start_time),
            ('create_date', '<=', end_time)
        ])

        # Get the list of partner_ids from the locations
        partner_ids_in_locations = locations.mapped('partner_id').ids

        # Query res.users and check if partner_id is not in the partner_ids_in_locations
        missing_users = self.env['res.users'].search([
            ('partner_id', 'not in', partner_ids_in_locations),
            ('employee_ids', '!=', False),
            ('employee_ids.job_id.name', '=', 'Saleman')
        ])

        # Convert missing users to a set for quick lookup
        missing_user_ids = set(missing_users.mapped('id'))

        # Fetch all users
        all_users = self.env['res.users'].search([
            ('employee_ids', '!=', False),
            ('employee_ids.job_id.name', '=', 'Saleman')
        ])

        # Construct the message with missing users marked
        # message_lines = [f"{user.name} (Missing)" if user.id in missing_user_ids else user.name for user in all_users]

        message_lines = [
            f"{user.employee_ids[0].name} (Missing)" if user.id in missing_user_ids else user.employee_ids[0].name
            for user in all_users if user.employee_ids
        ]

        # Get the current date in DD/MM/YYYY format
        current_date = datetime.today().strftime('%d/%m/%Y')

        _logger.info(f"missing_users_data: {message_lines}")

        # Format the message for Line Notify
        message = f"Check-in Status ({current_date}):\n" + '\n'.join(message_lines)

        config_param = self.env['ir.config_parameter'].sudo()
        token = config_param.get_param('line.token', 'ajpyqgiSOyySwICIbN9qUMLtOtSPtvXmXRh8Kq3YrSVFV8x90wxwX4wfPf31syvmMgoSpvve3pxtWh1jsSZ/IsCtm3e4Wom3Yg0JZiCAVP2Iz1tJtSGL+9ppqwkPPqvAlpuVlErhpPHl4p++zQtXGgdB04t89/1O/w1cDnyilFU=')
        group_id = config_param.get_param('line.group.id', 'Ceb3ce658c6c89e938a9342a7e459699b')
        url = config_param.get_param('line.url', 'https://cat-api-dev.scapp.work/webhookvrd')

        # token = "ajpyqgiSOyySwICIbN9qUMLtOtSPtvXmXRh8Kq3YrSVFV8x90wxwX4wfPf31syvmMgoSpvve3pxtWh1jsSZ/IsCtm3e4Wom3Yg0JZiCAVP2Iz1tJtSGL+9ppqwkPPqvAlpuVlErhpPHl4p++zQtXGgdB04t89/1O/w1cDnyilFU="
        # url = "https://api.line.me/v2/bot/message/push"
        # url = "https://cat-api-dev.scapp.work/webhookvrd"
        headers = {
            "Authorization": "Bearer " + token,
            "content-type": "application/json"
        }
        body = {
            "to": group_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        response = requests.post(url, json=body, headers=headers)

        if response.status_code == 200:
            _logger.info(f"Response: {response.json()}")
            # print(response.json())  # Process the response data
        else:
            _logger.info(f"Error: {response.status_code}")
            # print(f"Error: {response.status_code}")



