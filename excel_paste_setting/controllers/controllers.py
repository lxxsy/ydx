# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError


class BeeServerExcelPaste(http.Controller):

    @http.route('/excel/paste', type='json', auth='user')
    def main(self, **kw):
        url = kw['url']
        url = url[1:-1]
        url = url.split('&')

        key = {'model': '', 'id': ''}
        for i in url:
            if i.split('=')[0] == 'model':
                key['model'] = i.split('=')[-1]
            if i.split('=')[0] == 'id':
                key['id'] = i.split('=')[-1]
        if not key['id']:
            return 'no'
        else:
            try:
                id = int(key['id'])
            except:
                return 'no'
        line_list = kw['data'].split('\r\n')
        if len(line_list) < 2:
            raise UserError('数据为空!')
        tag = kw['tag']
        header = line_list[0].split('\t')
        table_header = header
        res = self._check_model(key['model'],tag)
        data = self._get_data(table_header, line_list[1:-1], res, id)
        self._record_mothed(data, res)
        return 'yes'

    def _check_model(self, model,tag):
        setting = request.env['bee.server.excel.paste.setting'].sudo().search([('model_id.model', '=', model),('tag','=',tag)])
        if not setting or setting.model_id.model != model:
            raise UserError('模型 %s 不存在或者没有配置excel粘贴!' % model)
        res = {
            'model': setting.model_id.model,
            'model_line_field': setting.model_line_field_id.name,
            'foreign_model': setting.foreign_model_id.model,
            'foreign_model_line_field': setting.foreign_model_line_field_id.name,
            'key': {
                line.table_header: {
                    'type': line.field_ttype,
                    'name': line.field_id.name,
                    'model': line.field_id.relation,
                } for line in setting.line_ids.filtered(lambda x: x.is_paste == True)
            }
        }
        return res

    def _get_data(self, header, line_data, key_dict, id):
        key_order = {
            key: header.index(key) for key in header if key in key_dict['key']
        }
        data = []
        row = len(header)
        for line in line_data:
            line_val = line.split('\t')
            if len(line_val) < row:
                continue
            val_dict = {}
            for k, v in key_order.items():
                if line_val[v] in ['', None, ' ']:
                    continue
                val = self._format_val(
                    line_val[v],
                    key_dict['key'][k]['type'],
                    key_dict['key'][k]['model'],
                )
                if val:
                    val_dict[key_dict['key'][k]['name']] = val
            val_dict[key_dict['foreign_model_line_field']] = id
            data.append(val_dict)
        return data

    def _format_val(self, val, type, model):
        if type in ['char', 'text', 'selection']:
            try:
                val = str(val)
            except:
                raise UserError('数据不正确!')
        elif type in ['float', 'monetary']:
            try:
                val = float(val)
            except:
                raise UserError('数据不正确!')
        elif type == 'integer':
            try:
                val = int(val)
            except:
                raise UserError('数据不正确!')
        elif type == 'many2one' and model:
            try:
                res = request.env[model].sudo().search([('name','=',val)])
            except:
                raise UserError('数据不正确!')
            if res:
                val = res[0].id
            else:
                raise UserError('数据不存在!')
        return val

    def _record_mothed(self, data, setting):
        for val in data:
                request.env[setting['foreign_model']].sudo().create(val)