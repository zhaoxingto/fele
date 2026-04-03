<script setup lang="ts">
const items = [
  '供应商询价与采购申请统一入口',
  '采购单、到货单、退货单后续可在这里拆分',
  '后续可接入 AG Grid 采购单表格式录入'
];
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper">
      <div class="text-24px font-700 text-[#102a43]">采购管理</div>
      <div class="mt-8 text-14px leading-6 text-[#52606d]">围绕请购、下单、到货、退货建立采购业务闭环。</div>
    </NCard>

    <NCard :bordered="false" class="card-wrapper">
      <div class="mb-12 text-16px font-600 text-[#102a43]">当前规划</div>
      <div class="grid gap-12">
        <div v-for="item in items" :key="item" class="rounded-16px bg-[#f8fafc] p-14 text-14px text-[#334e68]">
          {{ item }}
        </div>
      </div>
    </NCard>
  </div>
</template>
