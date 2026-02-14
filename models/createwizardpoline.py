from odoo import models, fields, api
class CreatePOWizardLine(models.TransientModel):
    _name = 'create.po.wizard.line'
    _description = 'PO Line for Wizard'

    wizard_id = fields.Many2one('create.po.wizard')
    product_id = fields.Many2one('product.product', string="Product")
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Quantity", default=1.0)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    copy_description = fields.Boolean(string="Copy description to PO")
