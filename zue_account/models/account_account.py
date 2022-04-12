
from odoo import models, fields, api, _

#PLAN CONTABLE - PUC

class account_account(models.Model):
    _name = 'account.account'
    _inherit = ['account.account','mail.thread', 'mail.activity.mixin']

    required_analytic_account = fields.Boolean('Obliga cuenta analítica', tracking=True)
    required_partner = fields.Boolean('Obliga tercero', tracking=True)
    accounting_class = fields.Char('Clase', tracking=True)
    code = fields.Char(tracking=True)
    user_type_id = fields.Many2one(tracking=True)
    tax_ids = fields.Many2many(tracking=True)
    group_id = fields.Many2one(tracking=True)
    company_id = fields.Many2one(tracking=True)
    account_distribution = fields.Boolean(tracking=True)