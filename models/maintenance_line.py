from odoo import models, fields, api

class MaintenanceLine(models.Model):
    _name = 'maintenance.line'
    _description = 'Maintenance Ticket Line'

    ticket_id = fields.Many2one(
        'product.assigned',  # لاحظ الاسم الجديد
        string='Ticket',
        ondelete='cascade',
        required=False  # خليها False لتجنب خطأ Add Line قبل save
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )

    serial_number_id = fields.Many2one(
        'stock.lot',
        string='Serial Number',
        required=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.serial_number_id = False
                return {
                    'domain': {
                        'serial_number_id': [('product_id', '=', line.product_id.id)]
                    }
                }
            else:
                return {'domain': {'serial_number_id': []}}
