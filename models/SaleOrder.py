from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    maintenance_ticket_id = fields.Many2one('maintenance.ticket')

    quotation_type = fields.Selection([
        ('normal', 'Normal'),
        ('maintenance', 'Maintenance')
    ], default='normal')

    maintenance_product = fields.Many2one('product.product')
    serial_number = fields.Many2one('stock.lot')
    department = fields.Selection([
        ('sw', 'SW'),
        ('cc', 'CC'),
        ('cssd', 'CSSD'),
        ('others', 'Others')
    ])
