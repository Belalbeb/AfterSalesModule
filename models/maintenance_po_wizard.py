from odoo import models, fields, api

class CreatePOWizard(models.TransientModel):
    _name = 'create.po.wizard'
    _description = 'Create PO from Ticket'

    ticket_id = fields.Many2one('maintenance.ticket', string="Ticket")
    existing_po_id = fields.Many2one('purchase.order', string="Existing PO")
    match_by_date = fields.Boolean(string="Match existing PO lines by Scheduled Date")

    vendor_id = fields.Many2one('res.partner', string="Supplier", required=True)
    po_line_ids = fields.One2many('create.po.wizard.line', 'wizard_id', string="Products")

    def action_create_po(self):
        # create purchase order
        po_vals = {
            'partner_id': self.vendor_id.id,
            'maintenance_ticket_id': self.ticket_id.id,
            'po_type': 'maintenance',
        }
        po = self.env['purchase.order'].create(po_vals)

        # create lines
        for line in self.po_line_ids:
            self.env['purchase.order.line'].create({
                'order_id': po.id,
                'product_id': line.product_id.id,
                'name': line.description,
                'product_qty': line.quantity,
                'product_uom': line.uom_id.id,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
        }
