from odoo import models, fields, api

class Device_Status(models.Model):
    _name = "device.status"
    _description = "Device Status"
    _order = 'sequence, id'
    
    name = fields.Char(string='Status Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    fold = fields.Boolean(string='Folded in Kanban', default=False)
    
    # Additional status flags (optional)
    device_is_out_of_order = fields.Boolean()
    device_under_testing = fields.Boolean()
    device_needs_spare_parts = fields.Boolean()
    device_is_working_properly = fields.Boolean()