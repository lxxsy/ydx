# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime

class SaleFactoryNo(models.Model):
    _name = "sale.designer"

    name = fields.Char(string=_("设计师"))
