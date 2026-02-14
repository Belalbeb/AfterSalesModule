from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)
class MaintenanceTicket(models.Model):
    _name = "maintenance.ticket"
    _description = "Maintenance Ticket"
    _rec_name = "description"
    _inherit = ['mail.thread', 'mail.activity.mixin']# This will be used as the display name
    
    
    
    # Basic Information
    name = fields.Char(string="Ticket Number",  copy=False, readonly=True, default='New')
    customer = fields.Many2one("res.partner", string="Customer")
    assigned_to = fields.Many2one("res.users", string="Assigned to")
    # Product Information
    part_number =fields.Char(string="Part Number")
    model = fields.Many2one("model.customize",  string="Model")
    maintenance_product=fields.Many2one("product.product",  string="Maintenance Product")
    serial_number = fields.Many2one("stock.lot", string="Serial Numbers")
    # Department
    department = fields.Selection([
        ('sw', 'SW'),
        ('cc', 'CC'),
        ('cssd', 'CSSD'),
        ('others', 'Others')
    ], string="Department")
    
 
   


    # Description
    description = fields.Char(string="Description")
    
    # Contact Information
    contact_name = fields.Many2one("res.partner", string="Contact Name")
    contact_position = fields.Many2one("hr.job", string="Contact Position")
    phone_number = fields.Char(string="Phone Number")
    
    # Ticket Category
    ticket_category = fields.Selection([
        ('ml', 'Malfunctions'),
        ('qr', 'Quotation Requests'),
        ('ins', 'Installations'),
        ('gi', 'General Inquiries'),
        ('rr', 'Training Request'),  # Fixed typo: 'raining' -> 'Training'
        ('ifr', 'Inspection Fees Request'),
        ('ppruw', 'PPM Product Request Under Warranty'),
        ('nd', 'Need a Document')
    ], string="Category")
    
    # Standard Odoo fields for tracking
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    stage_id = fields.Many2one(
        'maintenance.ticket.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
    )
    
    # Computed fields from stage for view visibility
    stage_need_visit = fields.Boolean(compute='_compute_stage_flags', string='Stage Need Visit', store=False)
    stage_need_quotation = fields.Boolean(compute='_compute_stage_flags', string='Stage Need Quotation', store=False)
    stage_need_po = fields.Boolean(compute='_compute_stage_flags', string='Stage Need PO', store=False)

    visit_count = fields.Integer(compute='_compute_visit_count')
    quotation_count = fields.Integer(compute='_compute_quotation_count')
    po_count=fields.Integer(compute='_compute_po_count')
    @api.depends('stage_id', 'stage_id.need_visit', 'stage_id.need_quotation', 'stage_id.need_po')
    def _compute_stage_flags(self):
        for rec in self:
            rec.stage_need_visit = rec.stage_id.need_visit if rec.stage_id else False
            rec.stage_need_quotation = rec.stage_id.need_quotation if rec.stage_id else False
            rec.stage_need_po = rec.stage_id.need_po if rec.stage_id else False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Return all stages, even if not used, for kanban group expansion"""
        return stages.search([], order=order)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.ticket') or 'New'
        
        if not vals.get('stage_id'):
           default_stage = self.env['maintenance.ticket.stage'].search([('is_default', '=', True)], limit=1)
           if default_stage:
              vals['stage_id'] = default_stage.id
           
       
        ticket = super().create(vals)
        if not ticket.maintenance_product or not ticket.serial_number:
           _logger.warning(
               "Ticket %s created without maintenance_product or serial_number",
               ticket.name
           )
           return ticket

        # Search in Product Assigned Engineer
        
        assigned = self.env['product.assigned'].search([
            ('department', '=', ticket.department),
            ('line_ids.product_id', '=', ticket.maintenance_product.id),
            ('line_ids.serial_number_id', '=', ticket.serial_number.id),
        ], limit=1)

     
        # Assignment Logic
        if ticket.department == 'cc':
            # Direct assignment to Engineer
            ticket.assigned_to = assigned.engineer
          

        elif ticket.department in ['sw', 'cssd']:
            # Assign to Line Manager
            ticket.assigned_to = assigned.line_manager

        return ticket
    def action_create_visit(self):
     self.ensure_one()
    #  ensure that object hold one record

     visit = self.env['maintenance.visit'].create({
        'ticket_id': self.id,
        'customer': self.customer.id,
        'department':self.department,
        'contact_name':self.contact_name.id,
        'mobile':self.phone_number,
        
    })

     return {
        'type': 'ir.actions.act_window',
        'res_model': 'maintenance.visit',
        'view_mode': 'form',
        'res_id': visit.id,
    }
    def action_create_quotation(self):
      self.ensure_one()

      quotation = self.env['sale.order'].create({
        'partner_id': self.customer.id,
        'maintenance_ticket_id': self.id,
        'quotation_type': 'maintenance',

        'maintenance_product': self.maintenance_product.id,
        'serial_number': self.serial_number.id,
        'department': self.department,
        'partner_shipping_id': self.contact_name.id,
        'client_order_ref': self.phone_number,
    })

      return {
        'type': 'ir.actions.act_window',
        'res_model': 'sale.order',
        'view_mode': 'form',
        'res_id': quotation.id,
    }
   
    def _compute_visit_count(self):
     for rec in self:
        rec.visit_count = self.env['maintenance.visit'].search_count([
            ('ticket_id', '=', rec.id)
        ])
       

    def _compute_quotation_count(self):
     for rec in self:
        rec.quotation_count = self.env['sale.order'].search_count([
            ('maintenance_ticket_id', '=', rec.id)
        ])
    def _compute_po_count(self):
     for rec in self:
        rec.po_count = self.env['sale.order'].search_count([
            ('maintenance_ticket_id', '=', rec.id)
        ])
        
        
    def action_create_po(self):
     self.ensure_one()
     return {
        'type': 'ir.actions.act_window',
        'name': 'Create RFQ',
        'res_model': 'purchase.order',
        'view_mode': 'form',
        'view_id': False,             # optional: default PO form
        'target': 'new',              # open as popup wizard
        'context': {
            'default_maintenance_ticket_id': self.id,  # link ticket
            'default_order_type': 'rfq',               # set as RFQ
            'default_state': 'draft',                  # ensure it's draft
        
        }
    }
    def action_view_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'res_model': 'maintenance.visit',
            'view_mode': 'tree,form',
            'domain': [('ticket_id', '=', self.id)],
            'target': 'current'
        }
        
    
    @api.model
    def _cron_notify_open_tickets_after_two_weeks(self):
        """CRON: Notify users about overdue maintenance tickets"""

        # --- DEBUG LOG (VERY IMPORTANT) ---
        _logger.warning("CRON STARTED SUCCESSFULLY")

        # 1️⃣ Time condition (1 minute for testing)
        limit_date = fields.Datetime.now() - timedelta(minutes=1)

        # 2️⃣ Get tickets
        tickets = self.env['maintenance.ticket'].sudo().search([
            ('create_date', '<=', limit_date),
            ('active', '=', True),
        ])

        _logger.warning("FOUND %s TICKETS", len(tickets))

        if not tickets:
            return

        # 3️⃣ Get groups
        admin_group = self.env.ref(
            'After_Sales.group_maintenance_administrator',
            raise_if_not_found=False
        )
        print(admin_group)
        manager_group = self.env.ref(
            'After_Sales.group_maintenance_line_manager',
            raise_if_not_found=False
        )

        if not admin_group and not manager_group:
            _logger.warning("NO GROUPS FOUND")
            return

        # 4️⃣ Collect users
        users = self.env['res.users']
        print(users)
        if admin_group:
            users |= admin_group.users
        if manager_group:
            users |= manager_group.users

        users = users.sudo()
        partner_ids = users.mapped('partner_id').ids

        _logger.warning("NOTIFYING %s USERS", len(users))

        if not partner_ids:
            return

        # 5️⃣ Notify per ticket
        for ticket in tickets:
            days_open = (fields.Datetime.now() - ticket.create_date).days

            # --- FOLLOWERS (MANDATORY) ---
            ticket.message_subscribe(partner_ids=partner_ids)

            # --- INBOX NOTIFICATION ---
            ticket.message_post(
                body=f"""
                <strong>⚠️ Overdue Maintenance Ticket</strong><br/>
                Ticket <b>{ticket.name}</b> has been open for
                <b style="color:red">{days_open} days</b>.
                """,
                subject=f"Overdue Ticket: {ticket.name}",
                partner_ids=partner_ids,
                subtype_id=self.env.ref('mail.mt_comment').id,
            )

            # --- ACTIVITY (TO-DO) ---
            for user in users:
                ticket.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    summary=f"Overdue Ticket: {ticket.name}",
                    note=f"Ticket {ticket.name} is overdue ({days_open} days). Please review.",
                )

        _logger.warning("CRON FINISHED SUCCESSFULLY")

    