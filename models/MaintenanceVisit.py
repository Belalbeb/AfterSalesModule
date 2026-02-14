from odoo import fields,api,models
from datetime import timedelta
class MaintenanceVisit(models.Model):
    _name = 'maintenance.visit'
    _description = 'Maintenance Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ticket_id = fields.Many2one('maintenance.ticket', required=True)
    customer = fields.Many2one('res.partner')
    department = fields.Selection([
        ('sw', 'SW'),
        ('cc', 'CC'),
        ('cssd', 'CSSD'),
        ('others', 'Others')
    ], string="Department")
    contact_name=fields.Many2one('res.partner')
    mobile=fields.Char()
    customer_type=fields.Selection([
        ('warranty','Warranty'),
        ('maintenance_contract','Maintenance Contract'),
        ('others','Others')
    ])
    visit=fields.Selection([
        ('service','Service'),
        ('inspection','Inspection'),
        ('supplying','Supplying'),
        ('installation','Installation')
    ])
    attachment=fields.Binary()
    work_description=fields.Text()
    visit_checklist_id=fields.One2many('visit.checklist','visit_id')
    device_is_out_of_order = fields.Boolean("Device is Out of Order")
    device_under_testing = fields.Boolean("Device Under Testing")
    device_needs_spare_parts = fields.Boolean("Device Needs Spare Parts")
    device_is_working_properly = fields.Boolean("Device is Working Properly")
    date = fields.Datetime(default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)

    def maintenance_visit_notification(self):
        today = fields.Datetime.now()

        # 1️⃣ Attachment Report Reminder (30 days)
        report_limit_date = today - timedelta(days=30)

        visits_no_report = self.sudo().search([
            ('date', '<=', report_limit_date),
            ('state', '=', 'done'),
            ('attachment', '=', False),
        ])

        admin_group = self.env.ref(
            'After_Sales.group_maintenance_administrator',
            raise_if_not_found=False
        )

        if admin_group:
            partners = admin_group.users.mapped('partner_id').ids
            for visit in visits_no_report:
                visit.message_subscribe(partner_ids=partners)
                visit.message_post(
                    body="⚠️ Attachment Report is missing for this visit (30 days passed)."
                )

        # 2️⃣ Unexecuted Visits - 1 Week
        one_week_date = today - timedelta(days=7)

        visits_1_week = self.sudo().search([
            ('date', '<=', one_week_date),
            ('state', '!=', 'done'),
        ])

        manager_group = self.env.ref(
            'After_Sales.group_maintenance_manager',
            raise_if_not_found=False
        )

        if manager_group:
            partners = manager_group.users.mapped('partner_id').ids
            for visit in visits_1_week:
                visit.message_subscribe(partner_ids=partners)
                visit.message_post(
                    body="⏰ Scheduled visit not executed after 1 week."
                )

        # 3️⃣ Unexecuted Visits - 2 Weeks
        two_weeks_date = today - timedelta(days=14)

        visits_2_weeks = self.sudo().search([
            ('date', '<=', two_weeks_date),
            ('state', '!=', 'done'),
        ])

        line_manager_group = self.env.ref(
            'After_Sales.group_maintenance_line_manager',
            raise_if_not_found=False
        )

        if line_manager_group:
            partners = line_manager_group.users.mapped('partner_id').ids
            for visit in visits_2_weeks:
                visit.message_subscribe(partner_ids=partners)
                visit.message_post(
                    body="🚨 Scheduled visit not executed after 2 weeks."
                )
                
            
            
        
       


