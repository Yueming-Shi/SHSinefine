# import logging

from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    def create_partner_site(selfs):
        for self in selfs.filtered(lambda s: s.site_id).mapped('site_id'):
            factor_arr = self.env['shipping.factor'].search(['|', ('name', '=', '普货'), ('name', '=', '敏感货')])
            for line in factor_arr:
                site_name = '%s-%s' % (self.name, line.name)
                site_partner_name = self.env['site.location'].search([('name', '=', site_name)])
                if not site_partner_name:
                    self.env['site.location'].create({
                        'name': site_name,
                        'factor_id': line.id,
                        'site_partner_id': self.id
                    })



