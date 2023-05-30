from odoo import models, fields, api, _


class ModificationFee(models.Model):
    _name = 'modification.fee'
    _description = '改泡费'

    name = fields.Char('名称')
    price = fields.Float('价格')

