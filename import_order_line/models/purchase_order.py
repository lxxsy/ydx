# -*- encoding: utf-8 -*-
import time, datetime
import math
from collections import defaultdict, OrderedDict
from operator import itemgetter
from itertools import groupby
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT as SD
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as ST
from odoo import models, fields, api, _, tools, SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from odoo.tools import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def action_open_import_purchase_order_line_wizard(self):
        """

        :return:
        """
        self.ensure_one()
        self._cr.commit()
        context = {}
        context.update(active_model=self._name,
                       active_ids=self.ids,
                       active_id=self.id,
                       )
        self.env.context = context
        wizard_id = self.env['import.purchase.order.line.wizard'].create(dict(master_id=self.id))
        return wizard_id.wizard_view()