<script setup lang="ts">
const cards = [
  { label: '今日订单', value: '18', note: '待审核 6 单' },
  { label: '待发货', value: '9', note: '优先处理加急订单' },
  { label: '已完成', value: '126', note: '本月累计' }
];
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper">
      <div class="text-24px font-700 text-[#102a43]">订单管理</div>
      <div class="mt-8 text-14px leading-6 text-[#52606d]">集中处理销售订单、履约状态和发货节奏。</div>
    </NCard>

    <NGrid cols="1 m:3" :x-gap="16" :y-gap="16" responsive="screen">
      <NGi v-for="item in cards" :key="item.label">
        <NCard :bordered="false" class="card-wrapper">
          <div class="text-12px tracking-[0.14em] text-[#7b8794]">{{ item.label }}</div>
          <div class="mt-10 text-28px font-700 text-[#102a43]">{{ item.value }}</div>
          <div class="mt-6 text-13px text-[#52606d]">{{ item.note }}</div>
        </NCard>
      </NGi>
    </NGrid>
  </div>
</template>
