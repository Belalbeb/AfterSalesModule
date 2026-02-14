from odoo import api,models,fields
class Product_Assigned_Engineer(models.Model):
    _name="product.assigned"
    _description="Product Assigned Engineer"
    engineer=fields.Many2one('res.users',string="Engineer")
    line_manager=fields.Many2one('res.users',string="Line Manager")
    department = fields.Selection([
        ('sw', 'SW'),
        ('cc', 'CC'),
        ('cssd', 'CSSD'),
        ('others', 'Others')
    ], string="Department")
    line_ids = fields.One2many(
        'maintenance.line',
        'ticket_id',
        string='Products & Serials'
    )

