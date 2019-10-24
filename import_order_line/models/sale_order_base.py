# -*- encoding: utf-8 -*-
# 外购表信息
OUTSOURCE_SHEET_NAME = 'Sheet1'
OUTSOURCE_HEADER_ROW = 1
OUTSOURCE_DATA_BEGIN_ROW = 2
OUTSOURCE_MAP = (
    {
      "col": 0,
      "attribute": 'product_id.name',
      "header": '归属',
      "required": 1,
      "type": "string"
    },
    {
      "col": 1,
      "attribute": 'product_name',
      "header": '名称',
      "required": 0,
      "type": "string"
    },
    {
      "col": 2,
      "attribute": 'door_type',
      "header": '门型',
      "required": 0,
      "type": "string"
    },
    {
      "col": 3,
      "attribute": 'color',
      "header": '颜色',
      "required": 0,
      "type": "string"
    },
    {
      "col": 4,
      "attribute": 'product_thick',
      "header": '厚',
      "required": 0,
      "type": "float"
    },
    {
      "col": 5,
      "attribute": 'product_height',
      "header": '高',
      "required": 0,
      "type": "float"
    },
    {
      "col": 6,
      "attribute": 'product_width',
      "header": '宽',
      "required": 0,
      "type": "float"
    },
    {
      "col": 7,
      "attribute": 'product_uom_qty',
      "header": '数量',
      "required": 1,
      "type": "float"
    },
    {
      "col": 8,
      "attribute": 'product_opento',
      "header": '开向',
      "required": 0,
      "type": "string"
    },
    {
      "col": 9,
      "attribute": 'note',
      "header": '备注',
      "required": 0,
      "type": "string"
    },
    {
      "col": 10,
      "attribute": 'id',
      "header": '系统编号',
      "required": 0,
      "type": "int"
    },
)
# 功能五金表信息
FMETAL_SHEET_NAME = '连接五金清单'
FMETAL_HEADER_ROW = 2
FMETAL_DATA_BEGIN_ROW = 3
FMETAL_MAP = (
    {
      "col": 0,
      "attribute": 'null',
      "header": '序号',
      "required": 0,
      "type": "string"
    },
    {
      "col": 1,
      "attribute": 'product_id.name',
      "header": '名称',
      "required": 1,
      "type": "string"
    },
    {
      "col": 2,
      "attribute": 'product_speci_type',
      "header": '规格',
      "required": 0,
      "type": "string"
    },
    {
      "col": 3,
      "attribute": 'product_uom.name',
      "header": '单位',
      "required": 0,
      "type": "string"
    },
    {
      "col": 4,
      "attribute": 'product_uom_qty',
      "header": '数量',
      "required": 1,
      "type": "float"
    },
    {
      "col": 5,
      "attribute": 'note',
      "header": '备注',
      "required": 0,
      "type": "string"
    },
    {
      "col": 6,
      "attribute": 'id',
      "header": '系统编号',
      "required": 0,
      "type": "int"
    },
)
