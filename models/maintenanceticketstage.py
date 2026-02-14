from odoo import models, fields

class MaintenanceTicketStage(models.Model):
    _name = 'maintenance.ticket.stage'
    _description = 'Maintenance Ticket Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    fold = fields.Boolean(string='Folded in Kanban')
    is_default = fields.Boolean(string='Default Stage')
      # Stage Actions
    need_visit = fields.Boolean(string='Need Visit')
    need_quotation = fields.Boolean(string='Need Quotation')
    need_po = fields.Boolean(string='Need PO')