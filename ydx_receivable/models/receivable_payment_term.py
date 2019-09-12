from odoo import models, fields


class YdxAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    screenshots_proof = fields.Binary(strint='screenshots proof')
