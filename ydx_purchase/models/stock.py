# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class YdxStockLocationRoute(models.Model):
    _inherit = "stock.location.route"
    purchase_return_selectable = fields.Boolean("Selectable on Purchase Return Order Line")


class YdxStockMove(models.Model):
    _inherit = "stock.move"
    purchase_reutrn_line_id = fields.Many2one('purchase.return.lines', 'Purchase Return Line')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(YdxStockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('purchase_reutrn_line_id')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(YdxStockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.purchase_reutrn_line_id.id)
        return keys_sorted

    def _get_related_invoices(self):
        """ Overridden from stock_account to return the customer invoices
        related to this stock move.
        """
        rslt = super(YdxStockMove, self)._get_related_invoices()
        invoices = self.mapped('picking_id.purchase_return_id.invoice_ids').filtered(lambda x: x.state not in ('draft', 'cancel'))
        rslt += invoices
        #rslt += invoices.mapped('refund_invoice_ids')
        return rslt

    def _assign_picking_post_process(self, new=False):
        super(YdxStockMove, self)._assign_picking_post_process(new=new)
        if new and self.purchase_reutrn_line_id and self.purchase_reutrn_line_id.purchase_return_id:
            self.picking_id.message_post_with_view(
                'mail.message_origin_link',
                values={'self': self.picking_id, 'origin': self.purchase_reutrn_line_id.purchase_return_id},
                subtype_id=self.env.ref('mail.mt_note').id)

    def _prepare_procurement_values(self):
        procurement_values = super(YdxStockMove, self)._prepare_procurement_values()
        if self.sale_order_id:
            procurement_values['sale_order_id'] = self.sale_order_id.id
        procurement_values['cabinet_no'] = self.cabinet_no
        procurement_values['material'] = self.material
        procurement_values['product_colour'] = self.product_colour
        procurement_values['product_length'] = self.length
        procurement_values['width'] = self.width
        procurement_values['thickness'] = self.thickness
        procurement_values['remarks'] = self.remarks
        procurement_values['product_opento'] = self.product_opento
        procurement_values['product_name'] = self.product_name
        procurement_values['product_speci_type'] = self.product_speci_type
        procurement_values['sub_sale_order_no'] = self.sub_sale_order_no
        procurement_values['outsource_quantity'] = self.outsource_quantity
        return procurement_values


class YdxProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    purchase_return_id = fields.Many2one('purchase.return', 'Purchase Resturn Order')


class YdxStockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(YdxStockRule, self)._get_custom_move_fields()
        fields += ['purchase_line_id', 'partner_id', 'sub_sale_order_no']
        return fields


class YdxStockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_return_id = fields.Many2one(related="group_id.purchase_return_id", string="Purchase Return Order", store=True, readonly=False)


    def _log_less_quantities_than_expected(self, moves):
        """ Log an activity on sale order that are linked to moves. The
        note summarize the real proccessed quantity and promote a
        manual action.

        :param dict moves: a dict with a move as key and tuple with
        new and old quantity as value. eg: {move_1 : (4, 5)}
        """

        def _keys_in_sorted(purchase_return_line):
            """ sort by order_id and the sale_person on the order """
            return (purchase_return_line.purchase_return_id.id, purchase_return_line.purchase_return_id.user_id.id)

        def _keys_in_groupby(purchase_return_line):
            """ group by order_id and the sale_person on the order """
            return (purchase_return_line.purchase_return_id, purchase_return_line.purchase_return_id.user_id)

        def _render_note_exception_quantity(moves_information):
            """ Generate a note with the picking on which the action
            occurred and a summary on impacted quantity that are
            related to the sale order where the note will be logged.

            :param moves_information dict:
            {'move_id': ['sale_order_line_id', (new_qty, old_qty)], ..}

            :return: an html string with all the information encoded.
            :rtype: str
            """
            origin_moves = self.env['stock.move'].browse([move.id for move_orig in moves_information.values() for move in move_orig[0]])
            origin_picking = origin_moves.mapped('picking_id')
            values = {
                'origin_moves': origin_moves,
                'origin_picking': origin_picking,
                'moves_information': moves_information.values(),
            }
            return self.env.ref('purchase_stock.exception_on_picking').render(values=values)

        # documents = self._log_activity_get_documents(moves, 'purchase_return_line_id', 'DOWN', _keys_in_sorted, _keys_in_groupby)
        # self._log_activity(_render_note_exception_quantity, documents)

        return super(YdxStockPicking, self)._log_less_quantities_than_expected(moves)


class YdxProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    purchaes_return_order_ids = fields.Many2many('purchase.retrun', string="Purchase Return Orders", compute='_compute_purchaes_return_order_ids')
    purchaes_return_order_count = fields.Integer('Purchase return order count', compute='_compute_purchaes_return_order_ids')

    @api.depends('name')
    def _compute_purchaes_return_order_ids(self):
        for lot in self:
            stock_moves = self.env['stock.move.line'].search([
                ('lot_id', '=', lot.id),
                ('state', '=', 'done')
            ]).mapped('move_id').filtered(
                lambda move: move.picking_id.location_dest_id.usage == 'customer' and move.state == 'done')
            lot.purchaes_return_order_ids = stock_moves.mapped('purchase_return_line_id.purchase_return_id')
            lot.purchaes_return_order_count = len(lot.purchaes_return_order_ids)

    def action_view_pr(self):
        self.ensure_one()
        action = self.env.ref('purchase.action_orders').read()[0]
        action['domain'] = [('id', 'in', self.mapped('purchaes_return_order_ids.id'))]
        return action
