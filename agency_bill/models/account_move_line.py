# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from datetime import date
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    city_transfer_stock_move_id = fields.Many2one('stock.move', '内部调拨作业明细')

    city_transfer_reverse_bill_line_source_id = fields.Many2one('account.move.line', '调拨红冲凭证来源明细')
    city_transfer_reverse_bill_line_ids = fields.One2many('account.move.line',
                                                          'city_transfer_reverse_bill_line_source_id', '调拨红冲凭证明细')
    city_commission_bill_line_source_id = fields.Many2one('account.move.line', '月末绩效凭证来源明细')
    city_commission_bill_line_ids = fields.One2many('account.move.line',
                                                    'city_commission_bill_line_source_id', '月末绩效凭证明细')


    def multi_create_city_commission_bill(selfs, city_agency):
        _today = date.today()
        account_line_values_list = selfs.multi_prepare_city_commission_bill_line_values_list(city_agency)

        bill = selfs.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': city_agency.id,
            'line_ids': [(0, 0, values) for values in account_line_values_list],
            'ref': ','.join(selfs.mapped('move_id.name')),
            'invoice_date': _today,
        })
        bill.save_whitelist_lines()
        return bill

    def multi_prepare_city_commission_bill_line_values_list(selfs, city_agency):
        valid_selfs = selfs.filtered(lambda s:s.can_create_city_commission_bill_lines())
        if not valid_selfs:
            raise UserError('不存在有效的发票明细可以开票')

        values_list, account_move_type = [], 'in_invoice'
        for self in valid_selfs:
            values_list += self._prepare_city_transfer_reverse_line_values_list(city_agency, account_move_type)
            values_list += self._prepare_city_commission_line_values_list(city_agency, account_move_type)
        return values_list

    def can_create_city_commission_bill_lines(self):
        return all([
            self.sale_line_ids,
            not self.city_transfer_reverse_bill_line_ids,
            not self.city_commission_bill_line_ids,
        ])

    def _prepare_city_transfer_reverse_line_values_list(self, city_agency, account_move_type):
        product, quantity = self.product_id, self.quantity
        price_unit = city_agency.property_product_pricelist.get_product_price(product, quantity, city_agency)

        values = {
            'price_unit': price_unit,
            'quantity': quantity,
            'invoice_account': city_agency.property_account_transfer_id,
            'line_account': city_agency.property_account_payable_id,
            'product': self.product_id,
            'name': self.product_id.display_name,
            'partner': city_agency,
        }

        extra_invoice_values = {
            'city_transfer_reverse_bill_line_source_id': self.id,
        }
        extra_line_values = {}
        self_values_list = self.env['account.move.line'].model_prepare_values_list(
            account_move_type, values, extra_invoice_values, extra_line_values)
        return self_values_list


    def _prepare_city_commission_line_values_list(self, city_agency, account_move_type):
        values = {
            'price_unit': self.price_unit * self.quantity,
            'quantity': city_agency.city_commission_rate / 100,
            'invoice_account': city_agency.property_account_commission_id,
            'line_account': city_agency.property_account_payable_id,
            'product': self.env['product.product'],
            'name': f'{self.product_id.display_name} commission',
            'partner': city_agency,
        }

        extra_invoice_values = {
            'city_commission_bill_line_source_id': self.id,
        }
        extra_line_values = {}

        self_values_list = self.env['account.move.line'].model_prepare_values_list(
            account_move_type, values, extra_invoice_values, extra_line_values)
        return self_values_list

    @api.model
    def model_prepare_values_list(cls, account_move_type, values, extra_invoice_values={}, extra_line_values={}):
        keys = ('price_unit', 'quantity', 'invoice_account', 'line_account', 'product')
        price_unit, quantity, invoice_account, line_account, product = [
            values[key] for key in keys]

        amount = price_unit * quantity
        if account_move_type in ['out_invoice','in_refund']:
            invoice_credit, invoice_debit = amount, 0.0
        if account_move_type in ['in_invoice','out_refund']:
            invoice_credit, invoice_debit = 0.0, amount

        common_values = {
            'name': values['name'],
            'partner_id': values['partner'].id,
        }
        invoice_values = dict({
            'credit': invoice_credit,
            'debit': invoice_debit,
            'account_id': invoice_account.id,
            'price_unit': price_unit,
            'quantity': quantity,
            'product_id': product.id,
            'product_uom_id': product.uom_id.id,
        }, **common_values, **extra_invoice_values)

        line_values = dict({
            'credit': invoice_debit,
            'debit': invoice_credit,
            'account_id': line_account.id,
            'price_unit': amount,
            'quantity': 1.0,
            'exclude_from_invoice_tab': True,
        }, **common_values, **extra_line_values)

        return [invoice_values, line_values]

