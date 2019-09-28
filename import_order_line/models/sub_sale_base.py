# -*- encoding: utf-8 -*-
# 外购表信息
OUTSOURCE_SHEET_NAME = '外购清单'
OUTSOURCE_HEADER_ROW = 1
OUTSOURCE_DATA_BEGIN_ROW = 2
OUTSOURCE_MAP = (
    {
      "col": 0,
      "attribute": 'product_id.name',
      "header": '名称'
    },
    {
      "col": 1,
      "attribute": 'product_speci_type',
      "header": '门型'
    },
    {
      "col": 2,
      "attribute": 'color',
      "header": '颜色'
    },
    {
      "col": 3,
      "attribute": 'product_thick',
      "header": '厚'
    },
    {
      "col": 4,
      "attribute": 'product_height',
      "header": '高'
    },
    {
      "col": 5,
      "attribute": 'product_width',
      "header": '宽'
    },
    {
      "col": 6,
      "attribute": 'product_uom_qty',
      "header": '数量'
    },
    {
      "col": 7,
      "attribute": 'product_opento',
      "header": '开向'
    },
    {
      "col": 8,
      "attribute": 'note',
      "header": '备注'
    },
    {
      "col": 9,
      "attribute": 'id',
      "header": '系统编号'
    },
)
# 功能五金表信息
FMETAL_SHEET_NAME = '功能五金清单'
FMETAL_HEADER_ROW = 2
FMETAL_DATA_BEGIN_ROW = 3
FMETAL_MAP = (
    {
      "col": 1,
      "attribute": 'product_id.name',
      "header": '名称'
    },
    {
      "col": 2,
      "attribute": 'product_speci_type',
      "header": '型号'
    },
    {
      "col": 3,
      "attribute": 'product_uom.name',
      "header": '单位'
    },
    {
      "col": 4,
      "attribute": 'product_uom_qty',
      "header": '数量'
    },
    {
      "col": 5,
      "attribute": 'note',
      "header": '备注'
    },
    {
      "col": 6,
      "attribute": 'id',
      "header": '系统编号'
    },
)

# 生产部件表信息
PRODUCTION_SHEET_NAME = '生产部件清单'
PRODUCTION_HEADER_ROW = 1
PRODUCTION_DATA_BEGIN_ROW = 2
PRODUCTION_MAP = (
    {
      "col": 0,
      "attribute": 'cabinet_no',
      "header": '订单柜号'
    },
    {
      "col": 1,
      "attribute": 'product_id.name',
      "header": '构件名称'
    },
    {
      "col": 2,
      "attribute": 'product_material',
      "header": '物料材质'
    },
    {
      "col": 3,
      "attribute": 'product_color',
      "header": '构件颜色'
    },
    {
      "col": 4,
      "attribute": 'product_length',
      "header": '成品长'
    },
    {
      "col": 5,
      "attribute": 'product_width',
      "header": '成品宽'
    },
    {
      "col": 6,
      "attribute": 'product_thick',
      "header": '成品厚'
    },
    {
      "col": 7,
      "attribute": 'material_use',
      "header": '物料用量'
    },
    {
      "col": 8,
      "attribute": 'material_open_length',
      "header": '开料长'
    },
    {
      "col": 9,
      "attribute": 'material_open_width',
      "header": '开料宽'
    },
    {
      "col": 10,
      "attribute": 'product_uom_qty',
      "header": '数量'
    },
    {
      "col": 11,
      "attribute": 'band_side',
      "header": '部件封边方式'
    },
    {
      "col": 12,
      "attribute": 'barcode',
      "header": '条形码'
    },
    {
      "col": 13,
      "attribute": 'note',
      "header": '备注'
    },
    {
      "col": 14,
      "attribute": 'id',
      "header": '系统编号'
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
      "header": '柜号'
    },
    {
      "col": 1,
      "attribute": 'product_id.name',
      "header": '名称'
    },
    {
      "col": 2,
      "attribute": '',
      "header": 'ERP编码'
    },
    {
      "col": 3,
      "attribute": '',
      "header": '品牌'
    },
    {
      "col": 4,
      "attribute": '',
      "header": '颜色'
    },
    {
      "col": 5,
      "attribute": 'product_speci_type',
      "header": '规格型号'
    },
    {
      "col": 6,
      "attribute": '',
      "header": '拓展属性'
    },
    {
      "col": 7,
      "attribute": 'product_uom_qty',
      "header": '数量'
    },
    {
      "col": 8,
      "attribute": 'product_uom.name',
      "header": '单位'
    },
    {
      "col": 9,
      "attribute": 'note',
      "header": '备注'
    },
    {
      "col": 10,
      "attribute": 'id',
      "header": '系统编号'
    },
)