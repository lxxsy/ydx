# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    legal_person = fields.Char(string=u'Legal Person')
    bank = fields.Char(string = 'account bank', help="account bank")
    bank_num = fields.Char(string = 'account bank number', help="account bank number")
    stamp_image = fields.Binary(
        "Stamp Image", attachment=True,
        help="This field holds the image used as image for the contract, limited to 1024x1024px.")
    dealer_id = fields.Many2one('res.users', '关联用户',)
    simple_name = fields.Char(string=u'简称')
