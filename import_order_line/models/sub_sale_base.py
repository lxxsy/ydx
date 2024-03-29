# -*- encoding: utf-8 -*-
# 外购表信息
OUTSOURCE_SHEET_NAME = '外购清单'
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
FMETAL_SHEET_NAME = '五金订单表'
FMETAL_HEADER_ROW = 2
FMETAL_DATA_BEGIN_ROW = 3
FMETAL_MAP = (
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
      "header": '型号',
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

# 生产部件表信息
PRODUCTION_SHEET_NAME = 'ERP中间表'
PRODUCTION_HEADER_ROW = 1
PRODUCTION_DATA_BEGIN_ROW = 2
PRODUCTION_MAP = (
    {
      "col": 0,
      "attribute": 'cabinet_no',
      "header": '订单柜号',
      "required": 0,
      "type": "string"
    },
    {
      "col": 1,
      "attribute": 'product_name',
      "header": '构件名称',
      "required": 0,
      "type": "string"
    },
    {
      "col": 2,
      "attribute": 'product_material',
      "header": '物料材质',
      "required": 0,
      "type": "string"
    },
    {
      "col": 3,
      "attribute": 'product_color',
      "header": '构件颜色',
      "required": 0,
      "type": "string"
    },
    {
      "col": 4,
      "attribute": 'product_length',
      "header": '成品长',
      "required": 0,
      "type": "float"
    },
    {
      "col": 5,
      "attribute": 'product_width',
      "header": '成品宽',
      "required": 0,
      "type": "float"
    },
    {
      "col": 6,
      "attribute": 'product_thick',
      "header": '成品厚',
      "required": 0,
      "type": "float"
    },
    {
      "col": 7,
      "attribute": 'material_use',
      "header": '物料用量',
      "required": 0,
      "type": "float"
    },
    {
      "col": 8,
      "attribute": 'material_open_length',
      "header": '开料长',
      "required": 0,
      "type": "float"
    },
    {
      "col": 9,
      "attribute": 'material_open_width',
      "header": '开料宽',
      "required": 0,
      "type": "float"
    },
    {
      "col": 10,
      "attribute": 'product_uom_qty',
      "header": '数量',
      "required": 1,
      "type": "float"
    },
    {
      "col": 11,
      "attribute": 'band_side',
      "header": '部件封边方式',
      "required": 0,
      "type": "string"
    },
    {
      "col": 12,
      "attribute": 'barcode',
      "header": '条形码',
      "required": 0,
      "type": "string"
    },
    {
      "col": 13,
      "attribute": 'note',
      "header": '备注',
      "required": 0,
      "type": "string"
    },
    {
      "col": 14,
      "attribute": 'id',
      "header": '系统编号',
      "required": 0,
      "type": "int"
    },
)

# 连接五金表信息
CMETAL_SHEET_NAME = '连接五金清单'
CMETAL_HEADER_ROW = 4
CMETAL_DATA_BEGIN_ROW = 5
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