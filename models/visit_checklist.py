from odoo import models, fields,api
class VisitChecklist(models.Model):
    _name = 'visit.checklist'
    _description = "Visit Checklist"

    visit_id = fields.Many2one('maintenance.visit', string="Maintenance Visit")
    part_number = fields.Char(string="Part Number")
    product_id = fields.Many2one('product.template', string="Product")
    model_id = fields.Many2one('model.customize', string="Model")
    product_family_id = fields.Many2one('product.family', string="Product Family")
    serial_number_ids = fields.Many2many('stock.lot', string="Serial Numbers")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.model_id = self.product_id.model_id.id if hasattr(self.product_id, 'model_id') else False
            self.product_family_id = self.product_id.product_family_id.id if hasattr(self.product_id, 'product_family_id') else False
            self.part_number = self.product_id.default_code
            # For serial numbers, you may filter stock.production.lot by product_id
            self.serial_number_ids = self.env['stock.lot'].search([('product_id', '=', self.product_id.id)])
