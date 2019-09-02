# -*- coding: utf-8 -*-

from odoo import models, fields, api
from addons.hr_expense.models import hr_expense
from dingding.dindin_workrecord.models import work_record
import socket



class ydx_perfect_dindin_workrecord(hr_expense.HrExpense,work_record.DinDinWorkRecordTemplate):

    _inherit = ['hr.expense','dindin.work.record.template']

    # date_approve  钉钉审批日期
    date_approve = fields.Date('Approval Date', readonly=1, index=True, copy=False)
    # # 获取本机名称
    # Local_name = fields.Char('本机名称', readonly=True, index=True, default=get_Local_name)
    # # 获取本机当前本机ip
    # Local_ip = fields.Char('本机ip', readonly=True,index=True, default=get_Local_ip)
    #钉钉待办用户
    emp_ids = fields.Many2many(comodel_name='hr.employee', string=u'待办用户', required=True)

    # 创建报表
    @api.multi
    def action_submit_sheet_ydx_dingding(self):
        tmp = super().action_submit_sheet()
        templates = self.env['dindin.work.record.template'].sudo()
        template = templates.get_template_by_type("hr_expense")
        if template:
            tmp_url = 'id=%s' % (self.id)
            formItemList = list()
            formItemList.append({
                'title': u"费用说明",
                'content': self.name,
            })
            formItemList.append({
                'title': u"申请人",
                'content': self.employee_id.name,
            })
            self.emp_ids = template.send_record_template(tmp_url,
                                                         formItemList,
                                                         u"费用订单审批",
                                                         u"hr_expense",
                                                         self.name,
                                                         self.emp_ids,
                                                         None)
        return tmp

    #审批按钮
    def approve_expense_sheets_ydx_dingding(self):
        tmp = super().approve_expense_sheets()
        templates = self.env['dindin.work.record.template'].sudo()
        template = templates.get_template_by_type("hr_expense")
        template.record_template_update('hr_expense', self.name, self.emp_ids)
        return tmp


    # #获取本机名称
    # @api.multi
    # def get_Local_name(self):
    #     for i in self:
    #         i.Local_name = socket.gethostname()
    #
    #
    # #获取当前本机id地址
    # @api.multi
    # def get_Local_ip(self):
    #     for i in self:
    #         i.Local_ip = socket.gethostbyname(Local_name)
