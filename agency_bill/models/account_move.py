# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    city_commission_bill_id = fields.Many2one('account.move','月末佣金凭证')
    partner_city_agency_id = fields.Many2one(related='partner_id.city_agency_id',string='城市代理',store=True)
    whitelist_lineIds = fields.Char()

    @api.depends('invoice_line_ids','partner_id','city_commission_bill_id')
    def _compute_can_create_city_commission_account_move(selfs):
        for self in selfs:
            self.can_create_city_commission_account_move = all([
                self.partner_city_agency_id,
                not self.city_commission_bill_id,
                # self.invoice_line_ids.mapped('sale_line_ids.order_id').website_id.should_city_agency_care,
            ])
    can_create_city_commission_account_move = fields.Boolean('待开月末佣金凭证',compute='_compute_can_create_city_commission_account_move',store=True)

    def multi_create_city_commission_bill(selfs):
        selfs._check_multi_create_city_commission_bill()
        city_agency = selfs.mapped('partner_id.city_agency_id')
        bill = selfs.mapped('invoice_line_ids').multi_create_city_commission_bill(city_agency)
        return selfs.action_view_commission_bill(bill)

    def _check_multi_create_city_commission_bill(selfs):
        if selfs.filtered(lambda s:not s.partner_city_agency_id):
            raise UserError('城市代理存在为空')
        if len(selfs.mapped('partner_city_agency_id')) > 1:
            raise UserError('城市代理存在不一致')

        invalid_selfs = selfs.filtered(lambda s: not s.can_create_city_commission_account_move)
        if invalid_selfs:
            raise UserError(f"{','.join(invalid_selfs.mapped('name'))} 不用开票")

    def action_view_commission_bill(self, force_bill=None):
        action = {
            'name': '结算凭证',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        bills = force_bill
        if len(bills) > 1:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', bills.ids)],
            })
        elif len(bills) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': bills.id,
            })
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def save_whitelist_lines(self):
        self.write({'whitelist_lineIds': ','.join([str(_id) for _id in self.line_ids.ids])})

    def multi_keep_whitelist_lines(selfs):
        for self in selfs.filtered(lambda s: s.whitelist_lineIds).with_context(force_delete=True):
            self.write({
                'line_ids': [(2,line.id) for line in self.line_ids if str(line.id) not in self.whitelist_lineIds.split(',')],
                'whitelist_lineIds': False,
            })

    def action_post(selfs):
        result = super().action_post()
        selfs.multi_keep_whitelist_lines()
        return result

