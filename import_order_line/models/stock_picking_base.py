# -*- encoding: utf-8 -*-
# 外购表信息

# 功能五金表信息
FMETAL_SHEET_NAME = '功能五金清单'
FMETAL_HEADER_ROW = 0
FMETAL_DATA_BEGIN_ROW = 1
FMETAL_MAP = (
    {
      "col": 0,
      "attribute": 'product_id.name',
      "header": '名称',
      "required": 1,
      "type": "string"
    },
    {
      "col": 1,
      "attribute": 'product_speci_type',
      "header": '型号',
      "required": 0,
      "type": "string"
    },
    {
      "col": 2,
      "attribute": 'product_uom.name',
      "header": '单位',
      "required": 0,
      "type": "string"
    },
    {
      "col": 3,
      "attribute": 'product_uom_qty',
      "header": '数量',
      "required": 1,
      "type": "float"
    },
    {
      "col": 4,
      "attribute": 'note',
      "header": '备注',
      "required": 0,
      "type": "string"
    },
    {
      "col": 5,
      "attribute": 'id',
      "header": '系统编号',
      "required": 0,
      "type": "int"
    },
)



# 连接五金表信息
CMETAL_SHEET_NAME = '连接五金清单'
CMETAL_HEADER_ROW = 0
CMETAL_DATA_BEGIN_ROW = 1
CMETAL_MAP = (
    {
      "col": 0,
      "attribute": 'cabinet_no',
      "header": '柜号',
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
      "attribute": '',
      "header": 'ERP编码',
      "required": 0,
      "type": "string"
    },
    {
      "col": 3,
      "attribute": '',
      "header": '品牌',
      "required": 0,
      "type": "string"
    },
    {
      "col": 4,
      "attribute": '',
      "header": '颜色',
      "required": 0,
      "type": "string"
    },
    {
      "col": 5,
      "attribute": 'product_speci_type',
      "header": '规格型号',
      "required": 0,
      "type": "string"
    },
    {
      "col": 6,
      "attribute": '',
      "header": '拓展属性',
      "required": 0,
      "type": "string"
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
      "attribute": 'product_uom.name',
      "header": '单位',
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