# -*- encoding: utf-8 -*-
# 外购表信息
PURCHASE_SHEET_NAME = '产品'
PURCHASE_HEADER_ROW = 0
PURCHASE_DATA_BEGIN_ROW = 1
PURCHASE_MAP = (
    {
      "col": 0,
      "attribute": 'sub_sale_order_no',
      "header": '子销售订单',
      "required": 0,
      "type": "string"
    },
    {
      "col": 1,
      "attribute": 'cabinet_no',
      "header": '订单柜号',
      "required": 0,
      "type": "string"
    },
    {
      "col": 2,
      "attribute": 'product_id.name',
      "header": '产品',
      "required": 1,
      "type": "string"
    },
    {
      "col": 3,
      "attribute": 'product_name',
      "header": '名称',
      "required": 0,
      "type": "string"
    },
    {
      "col": 4,
      "attribute": 'product_speci_type',
      "header": '规格型号',
      "required": 0,
      "type": "string"
    },
    {
      "col": 5,
      "attribute": 'material',
      "header": '材质',
      "required": 0,
      "type": "string"
    },
    {
      "col": 6,
      "attribute": 'product_colour',
      "header": '颜色',
      "required": 0,
      "type": "string"
    },
    {
      "col": 7,
      "attribute": 'product_length',
      "header": '成品长度',
      "required": 0,
      "type": "float"
    },
    {
      "col": 8,
      "attribute": 'width',
      "header": '成品宽度',
      "required": 0,
      "type": "float"
    },
    {
      "col": 9,
      "attribute": 'thickness',
      "header": '成品厚度',
      "required": 0,
      "type": "float"
    },
    {
      "col": 10,
      "attribute": 'outsource_quantity',
      "header": '委外数量',
      "required": 0,
      "type": "float"
    },
    {
      "col": 11,
      "attribute": 'band_number',
      "header": '封边信息',
      "required": 0,
      "type": "string"
    },
    {
      "col": 12,
      "attribute": 'product_qty',
      "header": '数量',
      "required": 1,
      "type": "float"
    },
    {
      "col": 13,
      "attribute": 'product_opento',
      "header": '开向',
      "required": 0,
      "type": "string"
    },
    {
      "col": 14,
      "attribute": 'remarks',
      "header": '备注',
      "required": 0,
      "type": "string"
    },
    {
      "col": 15,
      "attribute": 'price_unit',
      "header": '单价',
      "required": 1,
      "type": "float"
    },
    {
      "col": 16,
      "attribute": 'taxes_id.name',
      "header": '税率',
      "required": 0,
      "type": "string"
    },
    {
      "col": 17,
      "attribute": 'id',
      "header": '系统编号',
      "required": 0,
      "type": "int"
    },
)
