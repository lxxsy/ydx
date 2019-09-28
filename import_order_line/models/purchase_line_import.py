# -*- encoding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError
import base64
import xlrd
from ydxaddons.import_order_line.models.purchase_line_base import PURCHASE_SHEET_NAME,PURCHASE_HEADER_ROW,PURCHASE_DATA_BEGIN_ROW,\
     PURCHASE_MAP

class ImportPurchaseLineWizard(models.TransientModel):
    _name = 'import.purchase.line.wizard'
    _description = u"导入采购订单明细"

    master_id = fields.Many2one('purchase.order', u'采购订单编号', ondelete="cascade", readonly=True)
    excel_file = fields.Binary(u'Excel文件', filters='*.xls')
    filename = fields.Char(u'filename')
    method = fields.Selection([
        ('import', 'Import'),
        ('update', 'Update')
    ], string="Import Method", default='import', required=True)

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
        res = super(ImportPurchaseLineWizard, self).default_get(fields)
        active_id = self._context.get('active_id', False)
        if not active_id:
            return res
        res.update(master_id=active_id)
        return res

    def _get_domain(self, attrstring, value, product_domain, product_uom_domain, product_taxes_domain):
        attrlist = attrstring.split('.')
        is_domain = False
        if len(attrlist) == 2:
            is_domain = True
            if attrlist[0] == "product_id":
                product_domain.append((attrlist[1], '=', value))
            elif attrlist[0] == "product_uom":
                product_uom_domain.append((attrlist[1], '=', value))
            elif attrlist[0] == "taxes_id":
                product_taxes_domain.append((attrlist[1], '=', value))

        return is_domain

    def _seache_by_domain(self, model_name, domain):
        return self.env[model_name].search(domain, limit=1)

    def _get_datas(self, sheet, header_row, data_row, data_map, errors):
        tmp_map = []
        for col in range(0, sheet.ncols):
            value = sheet.cell_value(header_row, col)
            for m in data_map:
                if value == m.get('header'):
                    m['col'] = col
                    tmp_map.append(m)
        items = []
        for row in range(data_row, sheet.nrows):
            product_domain = []
            product_uom_domain = []
            product_taxes_domain = []

            item = dict(
                order_id = self.master_id.id,
            )
            for m in tmp_map:
                coln = m.get("col")
                if coln < sheet.ncols:
                    m_value = sheet.cell_value(row, coln)
                    attrsting = m.get("attribute")
                    is_domain= self._get_domain(attrsting, m_value, product_domain, product_uom_domain, product_taxes_domain)
                    if not is_domain:
                        item[attrsting] = m_value

            if product_domain:
                product_id = self._seache_by_domain("product.product", product_domain)
                if not product_id:
                    errors.append(u'{sheet}:第{rowvalue}行的产品名称，系统中不存在!'.format(sheet=sheet.name, rowvalue=row+1))
                else:
                    item["product_id"] = product_id.id
                    item['product_uom'] = product_id.product_tmpl_id.uom_po_id.id

            if product_uom_domain:
                product_uom = self._seache_by_domain('uom.uom', product_uom_domain)
                if not product_uom:
                    errors.append(u'{sheet}:第{rowvalue}行的单位名称，系统中不存在!'.format(sheet=sheet.name,rowvalue=row+1))
                else:
                    item["product_uom"] = product_uom.id

            if product_taxes_domain:
                product_taxes = self.env['account.tax'].search(product_taxes_domain)
                if not product_taxes:
                    errors.append(u'{sheet}:第{rowvalue}行的税率，系统中不存在!'.format(sheet=sheet.name,rowvalue=row+1))
                else:
                    item["taxes_id"] = [(6, 0,product_taxes.ids)]

            items.append(item)

        return items

    def _write_datas(self, model_name, line, datas):
        if self.method == "update":
            for data in datas:
                for l in line:
                    if int(data.get('id', -1)) == l.id:
                        l.write(data)
        elif self.method == "import":
            line.unlink()
            self.env[model_name].create(datas)

    @api.multi
    def action_confirm(self):
        self.ensure_one()

        if self.excel_file:
            excel = xlrd.open_workbook(file_contents=base64.decodebytes(self.excel_file))
            outsource_datas = []
            errors = []

            sheet = excel.sheet_by_name(PURCHASE_SHEET_NAME)
            if sheet:
                datas = self._get_datas(sheet, PURCHASE_HEADER_ROW, PURCHASE_DATA_BEGIN_ROW, PURCHASE_MAP, errors)

            if errors:
                raise UserError(u'表中数据有以下问题：\n {errors}'.format(errors='\n'.join(errors)))

            if datas:
                self._write_datas("purchase.order.line", self.master_id.order_line, datas)

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def wizard_view(self):
        view = self.env.ref('import_order_line.form_import_sub_sale_order_line_wizard')
        return {'name': _(u'导入订单明细'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.sub.sale.order.line.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': self.ids[0],
                'context': self.env.context}