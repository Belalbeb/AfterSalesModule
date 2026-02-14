from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    maintenance_ticket_id = fields.Many2one('maintenance.ticket')
    po_type = fields.Selection([
        ('normal', 'Normal'),
        ('maintenance', 'Maintenance')
    ], default='normal')
