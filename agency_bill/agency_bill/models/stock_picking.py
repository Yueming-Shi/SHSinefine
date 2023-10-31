# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _compute_city_transfer_bill_ids(selfs):
        for self in selfs:
            self.city_transfer_bill_ids = self.move_lines.mapped('city_transfer_bill_line_ids.move_id')
    city_transfer_bill_ids = fields.Many2many('account.move', 'stock_picking_city_transfer_bill_rel',
                    'picking_id', 'move_id', '城市代理调拨凭证', compute='_compute_city_transfer_bill_ids')



    @api.depends('city_transfer_bill_ids')
    def _compute_bill_ids(selfs):
        for self in selfs:
            self.bill_ids = self.city_transfer_bill_ids
    bill_ids = fields.Many2many('account.move',compute='_compute_bill_ids')

    @api.depends('bill_ids')
    def _compute_bills_count(selfs):
        for self in selfs:
            self.bills_count = len(self.bill_ids)
    bills_count = fields.Integer(compute='_compute_bills_count')

    def _action_done(self):
        result = super()._action_done()
        city_agency, moves = self.partner_id.filtered(lambda p:p.is_city_agency), \
            self.move_lines.filtered(lambda m:m.state == 'done')
        if all([city_agency, moves]):
            bill = moves.multi_create_city_transfer_bill(city_agency)
            bill.action_post()
            self.clear_anglo_saxon_lines(bill)
        return result

    def action_view_bills(self):
        action = {
            'name': '结算凭证',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        bills = self.bill_ids
        if len(bills) > 1:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id','in',bills.ids)],
            })
        elif len(bills) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': bills.id,
            })
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def clear_anglo_saxon_lines(self, bill):
        categs = self.move_lines.mapped('product_id.categ_id')
        accounts = categs.mapped('property_account_expense_categ_id') | categs.mapped('property_stock_account_output_categ_id')
        bill.line_ids.filtered(lambda l:l.account_id in accounts).with_context(force_delete=True).unlink()

