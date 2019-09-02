# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class YdxSaleStockLocationRoute(models.Model):
    _inherit = "stock.location.route"
    sale_return_selectable = fields.Boolean("Selectable on Sales Order Line")


class YdxSaleStockMove(models.Model):
    _inherit = "stock.move"
    sale_return_line_id = fields.Many2one('sale.return.line', 'Sale Return Line')

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(YdxSaleStockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('sale_return_line_id')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(YdxSaleStockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.sale_return_line_id.id)
        return keys_sorted

    def _get_related_invoices(self):
        """ Overridden from stock_account to return the customer invoices
        related to this stock move.
        """
        rslt = super(YdxSaleStockMove, self)._get_related_invoices()
        invoices = self.mapped('picking_id.sale_return_id.invoice_ids').filtered(lambda x: x.state not in ('draft', 'cancel'))
        rslt += invoices
        #rslt += invoices.mapped('refund_invoice_ids')
        return rslt

    def _assign_picking_post_process(self, new=False):
        super(YdxSaleStockMove, self)._assign_picking_post_process(new=new)
        if new and self.sale_return_line_id and self.sale_return_line_id.order_id:
            self.picking_id.message_post_with_view(
                'mail.message_origin_link',
                values={'self': self.picking_id, 'origin': self.sale_return_line_id.order_id},
                subtype_id=self.env.ref('mail.mt_note').id)


class YdxSaleProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    sale_return_id = fields.Many2one('sale.return', 'Sale Return')


class YdxSaleStockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(YdxSaleStockRule, self)._get_custom_move_fields()
        fields += ['sale_return_line_id', 'partner_id']
        return fields


class YdxSaleStockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_return_id = fields.Many2one(related="group_id.sale_return_id", string="Sales Return", store=True, readonly=False)


    def _log_less_quantities_than_expected(self, moves):
        """ Log an activity on sale order that are linked to moves. The
        note summarize the real proccessed quantity and promote a
        manual action.

        :param dict moves: a dict with a move as key and tuple with
        new and old quantity as value. eg: {move_1 : (4, 5)}
        """

        def _keys_in_sorted(sale_return_id):
            """ sort by order_id and the sale_person on the order """
            return (sale_return_id.order_id.id, sale_return_id.order_id.user_id.id)

        def _keys_in_groupby(sale_return_id):
            """ group by order_id and the sale_person on the order """
            return (sale_return_id.order_id, sale_return_id.order_id.user_id)

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
            return self.env.ref('sale_stock.exception_on_picking').render(values=values)

        documents = self._log_activity_get_documents(moves, 'sale_return_line_id', 'DOWN', _keys_in_sorted, _keys_in_groupby)
        self._log_activity(_render_note_exception_quantity, documents)

        return super(YdxSaleStockPicking, self)._log_less_quantities_than_expected(moves)

class YdxSaleProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    sale_return_ids = fields.Many2many('sale.return', string="Sales Returns", compute='_compute_sale_return_ids')
    sale_return_count = fields.Integer('Sale return count', compute='_compute_sale_return_ids')

    @api.depends('name')
    def _compute_sale_return_ids(self):
        for lot in self:
            stock_moves = self.env['stock.move.line'].search([
                ('lot_id', '=', lot.id),
                ('state', '=', 'done')
            ]).mapped('move_id')
            stock_moves = stock_moves.search([('id', 'in', stock_moves.ids)]).filtered(
                lambda move: move.picking_id.location_dest_id.usage == 'customer' and move.state == 'done')
            lot.sale_return_ids = stock_moves.mapped('sale_return_line_id.order_id')
            lot.sale_return_count = len(lot.sale_return_ids)

    def action_view_return(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = [('id', 'in', self.mapped('sale_order_ids.id'))]
        return action
