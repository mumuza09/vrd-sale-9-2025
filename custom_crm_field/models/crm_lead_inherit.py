from odoo import models, fields, api, SUPERUSER_ID,_
import logging
_logger = logging.getLogger(__name__)
from markupsafe import Markup
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class CRMLead(models.Model):
    _inherit = "crm.lead"

    AVAILABLE_PRIORITIES = [
        ('0', 'Low'),
        ('1', 'Cold'),  # Medium > Cold
        ('2', 'Warm'),  # High > Warm
        ('3', 'Hot'),   # Very High > Hot
    ]

    priority = fields.Selection(
        AVAILABLE_PRIORITIES, string='Priority', index=True,
        default=AVAILABLE_PRIORITIES[0][0]
    )
    page_id = fields.Many2one('crm.page', string='Page')
    
    status = fields.Selection([
        ('appointment', 'Appointment'),
        ('follow_up', 'Follow Up'),
        ('disqualify', 'Disqualify'),
    ], string='Status')
    
    status_detail = fields.Selection([
        ('appointment', 'Appointment'),
        ('under_construction', 'Under Construction'),
        ('unmatch_type_of_work', 'Unmatch Type of Work'),
        ('suspended', 'Suspended'),
        ('unmatch_budget', 'Unmatch Budget'),
        ('couldnt_reach', 'Couldn\'t Reach'),
        ('other_province', 'Other Province'),
        ('exploring', 'Exploring'),
        ('follow_up_soon', 'Follow Up Soon'),
        ('follow_up_1', 'Follow Up 1'),
        ('follow_up_2', 'Follow Up 2'),
        ('follow_up_3', 'Follow Up 3'),
        ('call_again', 'Call Again'),
        ('no_respond', 'No Respond'),
        ('other', 'Other')
    ])

    furniture_select = fields.Selection(  [
            ('1', 'ตู้เสื้อผ้า'),
            ('2', 'โต๊ะเครื่องแป้ง'),
            ('3', 'เฟอร์์นิเจอร์ห้องนอน'),
            ('4', 'อื่นๆ')]
    )

    description = fields.Html('Notes')
    
    sales_staff = fields.Many2one(
        string="Sale Assistance",
        comodel_name='hr.employee',
        store=True, precompute=True, tracking=True)
    
    inactive_date = fields.Date(string="Inactive Date")
    leads_date = fields.Date(string="Leads Date")
    appointment_date = fields.Date(string="Appointment Date")
    visit_date = fields.Date(string="Visit Date")
    visit2_date = fields.Date(string="Visit 2 Date")
    debrief_date = fields.Date(string="Debrief Date")
    design_date = fields.Date(string="Design Date")
    design2_date = fields.Date(string="Design 2 Date")
    design3_date = fields.Date(string="Design 3 Date")
    quotation_date = fields.Date(string="Quotation Date")
    deposit_date = fields.Date(string="Deposit Date")
    production_date = fields.Date(string="Production Date")
    installation_date = fields.Date(string="Installation Date")
    final_payment_date = fields.Date(string="Final Payment Date")

    estimated_project_price = fields.Float(string="Estimated Project Price (THB)")
    actual_project_price = fields.Float(string="Actual Project Price (THB)")
    deposit_collected = fields.Float(string="Deposit Collected (THB)")
    final_payment_collected = fields.Float(string="Final Payment Collected (THB)")
    percentage_money_collected = fields.Float(string="Percentage Money Collected")

    @api.depends('company_id')
    def _compute_stage_domain(self):
        for rec in self:
            company_id = self.env.company.id 
            rec.stage_domain = [('company_id', '=', company_id)]
            
    stage_domain = fields.Char(compute="_compute_stage_domain", store=False)

    stage_id = fields.Many2one(
        'crm.stage', string='Stage', index=True, tracking=True,
        domain="stage_domain"
    )
    
    @api.model
    def _read_group_stage_ids(self, stages, domain):
        team_id = self._context.get('default_team_id')
        company_id = self.env.company.id

        if team_id:
            search_domain = [
                '|', ('id', 'in', stages.ids), 
                '|', ('team_id', '=', False), 
                ('team_id', '=', team_id)
            ]
        else:
            search_domain = [
                '|', ('id', 'in', stages.ids), 
                ('team_id', '=', False)
            ]

        search_domain.append(('company_id', '=', company_id))

        stage_ids = stages.sudo()._search(search_domain, order=stages._order)

        return stages.browse(stage_ids)



    def write(self, vals):
        stage_changed = 'stage_id' in vals and vals['stage_id'] != self.stage_id.id
        res = super().write(vals)
        if stage_changed:
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])
            new_stage_name = new_stage.name

            matched_key = None
            for key in sorted(self.noti_idmapp, key=len, reverse=True):
                if key in new_stage_name:
                    matched_key = key
                    break

            if matched_key:
                for lead in self:
                    if lead.user_id:
                        odoobot_id = self.env.ref("base.partner_root").id
                        user_partners = [lead.user_id.partner_id]
                        if lead.sales_staff:
                            user_partners.append(lead.sales_staff.user_partner_id)
                        for partner in user_partners:
                            channel = self.env['discuss.channel'].with_user(SUPERUSER_ID).channel_get([partner.id])
                            msglist = self.mapNotiMsg(new_stage_name,'change_stage',new_stage.company_id.name)
                            for msg in msglist:
                                channel.message_post(
                                    body= msg,
                                    author_id=odoobot_id,
                                    message_type="comment",
                                    subtype_xmlid="mail.mt_comment"
                                )
        return res
    

    noti_idmapp = {
        "Visit":{
            "stage_id" : 3,
            "on_stage_change": {
                "G7 Next": [6],
                "G7 Space": [0],
            },
            "on_stage_deadline": {
                "day" : 2,
                # "day" : 0,
                "G7 Next": [6],
                "G7 Space": [0],
            }
        },
        "Deposit":{
            "stage_id" : 0,
            "on_stage_change": {
                "G7 Next": [0],
                "G7 Space": [],
            },
            "on_stage_deadline": {
                "day" : 2,
                "G7 Next": [0],
                "G7 Space": [],
            }
        },
        "Design" : {
            "stage_id" : 7,
            "on_stage_change": {
                "G7 Next": [1,2],
                "G7 Space": [1,2],
            },
            "on_stage_deadline": {
                "day" : 1,
                # "day" : 0,
                "G7 Next": [1,2],
                "G7 Space": [1,2],
            }
        },
        "Quotation" : {
            "stage_id" : 10,
            "on_stage_change": {
                "G7 Next": [3],
                "G7 Space": [3],
            }
        },
        "Debrief" : {
            "stage_id" : 10,
            "on_stage_change": {
                "G7 Next": [],
                "G7 Space": [8],
            }
        },
        "Installation" : {
            "stage_id" : 10,
            "on_stage_change": {
                "G7 Next": [7],
                "G7 Space": [7],
            }
        },
        "Appointment" : {
            "stage_id" : 2,
            "on_stage_change": {
                "G7 Next": [4,5],
                "G7 Space": [4,5],
            },
            "on_stage_deadline": {
                "day" : 7,
                # "day" : 0,
                "G7 Next": [5],
                "G7 Space": [5],
            }
        },
    }
    pre_texy_noti = '<a href="%s">[%s]</a> <br/>'
    msg_list = [
        'กรุณา Debrief กับบริษัท G7 ภายใน 2 วัน',  
        'กรุณาติดต่ออัพเดทกับลูกค้า ภายใน 12 ชม. และหากมี feedback กรุณาอัพเดทกับทีมและ G7 ภายใน 1 ชม.',
        'หากไม่มีการแก้ไข Design กรุณาออก Quotation และ นัดลูกค้าเพื่อ Close Sales ภายใน 12 ชม.',
        'ติดตาม feedback และ การ Close Sales ให้แจ้งผลทันที',
        'กรณีลูกค้าเลื่อนขอเลื่อน Appointment และ ระบุวันนัดใหม่เลย ให้บันทึกวันนัดหมายใหม่ทันที',
        'กรณีลูกค้าขอเลื่อน Appointment แต่ยังไม่ระบุวัน ให้ติดตามเพื่อทำ Appointment ใหม่อีกครั้ง ภายใน 7 วัน',
        'กรุณาติดตามการวางมัดจำ หากมีการวางมัดจำเรียบร้อยแล้ว กรุณาย้าย Lead เป็น Deposit',
        'กรุณาติดตามการติดตั้งสินค้า',
        'หากได้รับ Debrief แล้ว กรุณาย้าย Lead เป็น Installation'

    ]

    def mapNotiMsg(self, val, type, company_name):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        lead_url = f'{base_url}/web#id={self.id}&model=crm.lead&view_type=form'
        _logger.info(f"Mapping notification messages for lead {self.name} with stage name {val} and type {type} for company {company_name}")

        msglist = []

        # ใช้ partial match กับ key ของ noti_idmapp
        matched_key = None
        for key in self.noti_idmapp:
            if key in val:
                matched_key = key
                break

        if matched_key:
            config = self.noti_idmapp[matched_key]
            if type == "change_stage":
                msg_indexes = config.get("on_stage_change", {}).get(company_name, [])
                for idx in msg_indexes:
                    if 0 <= idx < len(self.msg_list):
                        text = self.pre_texy_noti % (lead_url, self.name) + self.msg_list[idx]
                        msglist.append(Markup(text))

            elif type == "cron_stage":
                msg_indexes = config.get("on_stage_deadline", {}).get(company_name, [])
                for idx in msg_indexes:
                    if 0 <= idx < len(self.msg_list):
                        text = self.pre_texy_noti % (lead_url, self.name) + self.msg_list[idx]
                        msglist.append(Markup(text))
        else:
            _logger.warning(f"No matching config found in noti_idmapp for stage name '{val}'")

        return msglist


        
    def cron_check_stage_leads(self):
        _logger.info("Starting cron_check_stage_leads...")

        for stage_name, config in self.noti_idmapp.items():
            max_days = config.get("on_stage_deadline", {}).get("day")

            if max_days is None:
                _logger.warning(f"Missing deadline day for stage '{stage_name}'")
                continue

            stages = self.env['crm.stage'].search([('name', 'ilike', stage_name)])
            if not stages:
                _logger.warning(f"Stage not found for name: {stage_name}")
                continue
            for stage in stages:
                deadline = datetime.now() - timedelta(days=max_days)
                _logger.info(f"Checking leads in stage '{stage_name}' with deadline before {deadline.strftime('%Y-%m-%d %H:%M:%S')}")

                leads = self.env['crm.lead'].search([
                    ('stage_id', '=', stage.id),
                    ('date_last_stage_update', '<=', deadline),
                ])

                for lead in leads:
                    _logger.info(f"Processing lead: {lead.name} (ID: {lead.id})")

                    if lead.user_id:
                        odoobot_id = self.env.ref("base.partner_root").id
                        user_partners = [lead.user_id.partner_id]

                        if lead.sales_staff:
                            user_partners.append(lead.sales_staff.user_partner_id)

                        for partner in user_partners:
                            company_name = lead.company_id.name  # ← ใช้ company ของ lead
                            _logger.info(f"Sending message to partner: {partner.name} (ID: {partner.id}) for company {company_name}")
                            channel = self.env['discuss.channel'].with_user(SUPERUSER_ID).channel_get([partner.id])
                            msglist = lead.mapNotiMsg(stage_name, 'cron_stage', company_name)
                            for msg in msglist:
                                _logger.info(f"Posting message: {msg}")
                                channel.message_post(
                                    body=msg,
                                    author_id=odoobot_id,
                                    message_type="comment",
                                    subtype_xmlid="mail.mt_comment"
                                )

        _logger.info("Finished cron_check_stage_leads.")


    def get_column_field_mapping(self):
        return {
            'phone': 'phone',
            'contact_name': 'contact_name',
            'opportunity': 'name'
        }

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('import_file') or self.env.context.get('import_competition'):
            column_field_mapping = self.get_column_field_mapping()
            field1 = column_field_mapping['phone']
            field2 = column_field_mapping['contact_name']
            field3 = column_field_mapping['opportunity']  # ใช้ 'name' ตามที่คุณแมปไว้

            mapped_vals_list = [
                {column_field_mapping.get(k, k): v for k, v in original_vals.items()}
                for original_vals in vals_list
            ]

            from collections import Counter
            phone_counter = Counter(v.get(field1) for v in mapped_vals_list if v.get(field1))
            name_counter = Counter(v.get(field2) for v in mapped_vals_list if v.get(field2))

            duplicate_phones = {phone for phone, count in phone_counter.items() if count > 1}
            duplicate_names = {name for name, count in name_counter.items() if count > 1}

            db_duplicates_phone = set(
                self.search([(field1, 'in', list(duplicate_phones))]).mapped(field1)
            )
            db_duplicates_name = set(
                self.search([(field2, 'in', list(duplicate_names))]).mapped(field2)
            )

            all_dup_phones = duplicate_phones.union(db_duplicates_phone)
            all_dup_names = duplicate_names.union(db_duplicates_name)

            new_vals_list = []
            for vals in mapped_vals_list:
                val1 = vals.get(field1)
                val2 = vals.get(field2)
                val3 = vals.get(field3) or ''

                is_duplicate = (
                    (val1 and val1 in all_dup_phones) or
                    (val2 and val2 in all_dup_names)
                )

                if is_duplicate:
                    vals[field3] = f'Dup - {val3}'

                new_vals_list.append(vals)

            return super().create(new_vals_list)

        return super().create(vals_list)