# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from datetime import date
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    city_transfer_bill_line_ids = fields.One2many('account.move.line','city_transfer_stock_move_id')

    def multi_create_city_transfer_bill(selfs, city_agency):
        if selfs.filtered(lambda s:s.location_dest_id.is_city_agency):
            account_move_type = 'out_invoice'
        elif selfs.filtered(lambda s:s.location_id.is_city_agency):
            account_move_type = 'out_refund'
        else:
            raise UserError(f'作业明细 源位置、目的位置 请统一')

        _today = date.today()
        account_line_values_list = selfs.multi_prepare_city_transfer_bill_line_values_list(city_agency, account_move_type)
        bill = selfs.env['account.move'].create({
            'move_type': account_move_type,
            'partner_id': city_agency.id,
            'line_ids': [(0, 0, values) for values in account_line_values_list],
            'ref': ','.join(selfs.mapped('picking_id.name')),
            'invoice_date': _today,
        })
        bill.save_whitelist_lines()
        return bill

    def multi_prepare_city_transfer_bill_line_values_list(selfs, city_agency, account_move_type):
        values_list = []

        for self in selfs:
            product, quantity = self.product_id, self.quantity_done
            price_unit = city_agency.property_product_pricelist.get_product_price(product, quantity, city_agency)

            values = {
                'price_unit': price_unit,
                'quantity': quantity,
                'invoice_account': city_agency.property_account_transfer_id,
                'line_account': city_agency.property_account_receivable_id,
                'product': self.product_id,
                'name': self.name,
                'partner': city_agency,
            }

            extra_invoice_values = {
                'city_transfer_stock_move_id': self.id,
            }
            extra_line_values = {}

            self_values_list = selfs.env['account.move.line'].model_prepare_values_list(
                account_move_type, values, extra_invoice_values, extra_line_values)
            values_list += self_values_list

        return values_list
