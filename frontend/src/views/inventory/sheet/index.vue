<script setup lang="ts">
import { computed, ref } from 'vue';
import type { ColDef } from 'ag-grid-community';
import { AllCommunityModule, ModuleRegistry, themeQuartz } from 'ag-grid-community';
import { AgGridVue } from 'ag-grid-vue3';

ModuleRegistry.registerModules([AllCommunityModule]);

type SheetRow = {
  sku: string;
  name: string;
  warehouse: string;
  quantity: number;
  price: number;
  amount: number;
  remark: string;
};

const warehouseOptions = ['主仓', '华东仓', '门店A', '门店B'];

const localeText = {
  page: '页',
  more: '更多',
  to: '到',
  of: '共',
  next: '下一页',
  last: '末页',
  first: '首页',
  previous: '上一页',
  loadingOoo: '加载中...',
  selectAll: '全选',
  searchOoo: '搜索...',
  blanks: '空白',
  filterOoo: '筛选...',
  equals: '等于',
  notEqual: '不等于',
  empty: '请选择',
  lessThan: '小于',
  greaterThan: '大于',
  lessThanOrEqual: '小于等于',
  greaterThanOrEqual: '大于等于',
  inRange: '区间',
  contains: '包含',
  notContains: '不包含',
  startsWith: '开头是',
  endsWith: '结尾是',
  before: '早于',
  after: '晚于',
  andCondition: '且',
  orCondition: '或',
  applyFilter: '应用',
  resetFilter: '重置',
  clearFilter: '清除',
  cancelFilter: '取消',
  textFilter: '文本筛选',
  numberFilter: '数字筛选',
  dateFilter: '日期筛选',
  setFilter: '集合筛选',
  columns: '列',
  filters: '筛选',
  noRowsToShow: '暂无数据',
  pinColumn: '固定列',
  pinLeft: '固定到左侧',
  pinRight: '固定到右侧',
  noPin: '取消固定',
  autosizeThiscolumn: '自动调整本列',
  autosizeAllColumns: '自动调整全部列',
  resetColumns: '重置列',
  expandAll: '全部展开',
  collapseAll: '全部收起'
};

const columnDefs = ref<ColDef<SheetRow>[]>([
  { headerName: 'SKU', field: 'sku', minWidth: 140, editable: true, pinned: 'left' },
  { headerName: '商品名称', field: 'name', minWidth: 180, editable: true },
  {
    headerName: '仓库',
    field: 'warehouse',
    minWidth: 150,
    editable: true,
    cellEditor: 'agSelectCellEditor',
    cellEditorParams: { values: warehouseOptions }
  },
  { headerName: '数量', field: 'quantity', minWidth: 110, editable: true, type: 'numericColumn' },
  { headerName: '单价', field: 'price', minWidth: 120, editable: true, type: 'numericColumn' },
  {
    headerName: '金额',
    field: 'amount',
    minWidth: 130,
    valueGetter: params => Number(params.data?.quantity || 0) * Number(params.data?.price || 0),
    valueFormatter: params => `¥ ${Number(params.value || 0).toFixed(2)}`
  },
  { headerName: '备注', field: 'remark', minWidth: 200, editable: true, flex: 1 }
]);

const rowData = ref<SheetRow[]>([
  { sku: 'SKU-1001', name: '无线扫码枪', warehouse: '主仓', quantity: 6, price: 299, amount: 1794, remark: '' },
  { sku: 'SKU-1002', name: '标签打印机', warehouse: '华东仓', quantity: 3, price: 460, amount: 1380, remark: '加急入库' },
  { sku: 'SKU-1003', name: '热敏纸', warehouse: '门店A', quantity: 20, price: 12.5, amount: 250, remark: '' }
]);

const defaultColDef: ColDef = {
  sortable: true,
  resizable: true,
  filter: true
};

const totalAmount = computed(() => rowData.value.reduce((sum, item) => sum + item.quantity * item.price, 0));
const gridTheme = themeQuartz.withParams({
  accentColor: '#0f766e',
  browserColorScheme: 'light',
  borderColor: '#d9e2ec',
  columnBorder: true,
  fontFamily: 'inherit',
  headerBackgroundColor: '#f8fbfc',
  headerTextColor: '#102a43',
  rowBorder: true
});

function addRow() {
  rowData.value = [
    ...rowData.value,
    { sku: '', name: '', warehouse: '主仓', quantity: 1, price: 0, amount: 0, remark: '' }
  ];
}
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper">
      <div class="flex items-start justify-between gap-16">
        <div class="max-w-760px">
          <div class="text-20px font-600 text-[#102a43]">采购入库单</div>
          <div class="mt-8 text-14px leading-6 text-[#52606d]">
            使用表格式录入处理明细行，支持快速编辑、整列筛选和 Excel 粘贴。
          </div>
        </div>
        <div class="flex items-center gap-12">
          <NButton type="primary" @click="addRow">新增行</NButton>
          <NTag type="success" round>中文表格</NTag>
        </div>
      </div>
    </NCard>

    <NGrid cols="1 m:3" :x-gap="16" :y-gap="16" responsive="screen">
      <NGi>
        <NCard :bordered="false" class="card-wrapper">
          <div class="text-12px tracking-[0.14em] text-[#7b8794]">单据类型</div>
          <div class="mt-8 text-18px font-600 text-[#102a43]">采购入库</div>
        </NCard>
      </NGi>
      <NGi>
        <NCard :bordered="false" class="card-wrapper">
          <div class="text-12px tracking-[0.14em] text-[#7b8794]">明细行数</div>
          <div class="mt-8 text-18px font-600 text-[#102a43]">{{ rowData.length }}</div>
        </NCard>
      </NGi>
      <NGi>
        <NCard :bordered="false" class="card-wrapper">
          <div class="text-12px tracking-[0.14em] text-[#7b8794]">合计金额</div>
          <div class="mt-8 text-18px font-600 text-[#102a43]">¥ {{ totalAmount.toFixed(2) }}</div>
        </NCard>
      </NGi>
    </NGrid>

    <NCard :bordered="false" class="card-wrapper">
      <div class="mb-14 flex items-center justify-between gap-12">
        <div class="text-16px font-600 text-[#102a43]">入库明细</div>
        <div class="text-13px text-[#52606d]">支持固定 SKU 列、单元格编辑和仓库下拉选择。</div>
      </div>
      <div class="ag-theme-wrap h-[560px] w-full overflow-hidden rounded-16px border border-[#d9e2ec]">
        <AgGridVue
          class="block h-full w-full"
          :column-defs="columnDefs"
          :default-col-def="defaultColDef"
          :locale-text="localeText"
          :row-data="rowData"
          :theme="gridTheme"
          :single-click-edit="true"
          :stop-editing-when-cells-lose-focus="true"
        />
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.ag-theme-wrap :deep(.ag-root-wrapper) {
  border: 0;
}
</style>
