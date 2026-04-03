<script setup lang="ts">
const stats = [
  { label: 'Products', value: '128', note: '12 pending approval' },
  { label: 'Warehouses', value: '4', note: '2 region hubs + 2 stores' },
  { label: 'Pending Orders', value: '23', note: '9 purchases / 14 sales' },
  { label: 'Low Stock Alerts', value: '7', note: 'Replenishment suggested' }
];

const actions = [
  { title: 'Create purchase order', desc: 'Start inbound replenishment for suppliers.' },
  { title: 'Create sales order', desc: 'Capture customer demand and reserve stock.' },
  { title: 'Record stock in', desc: 'Handle receipts, returns and adjustment entries.' },
  { title: 'Record stock out', desc: 'Ship orders and sync warehouse deduction.' }
];
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper">
      <div class="flex-col gap-8">
        <div class="text-3xl font-600 text-[#102a43]">Inventory operations overview</div>
        <div class="max-w-720px text-15px text-[#486581]">
          A lightweight SaaS workspace for products, stock, purchasing and sales.
        </div>
      </div>
    </NCard>

    <NGrid cols="1 s:2 l:4" :x-gap="16" :y-gap="16" responsive="screen">
      <NGi v-for="item in stats" :key="item.label">
        <NCard :bordered="false" class="card-wrapper">
          <div class="flex-col gap-10">
            <div class="text-13px uppercase tracking-[0.16em] text-[#7b8794]">{{ item.label }}</div>
            <div class="text-32px font-700 text-[#0f172a]">{{ item.value }}</div>
            <div class="text-13px text-[#52606d]">{{ item.note }}</div>
          </div>
        </NCard>
      </NGi>
    </NGrid>

    <NGrid cols="1 l:2" :x-gap="16" :y-gap="16" responsive="screen">
      <NGi>
        <NCard :bordered="false" class="card-wrapper h-full">
          <div class="mb-16 flex items-center justify-between">
            <div>
              <div class="text-18px font-600 text-[#102a43]">Quick Actions</div>
              <div class="mt-6 text-13px text-[#52606d]">Common operational entry points for the team.</div>
            </div>
            <NTag type="success" round>Fele ERP</NTag>
          </div>
          <div class="grid gap-12 md:grid-cols-2">
            <div
              v-for="item in actions"
              :key="item.title"
              class="rounded-16px border border-[#d9e2ec] bg-[#f8fbfc] p-16 transition-all duration-200 hover:border-[#0f766e] hover:bg-white"
            >
              <div class="text-15px font-600 text-[#102a43]">{{ item.title }}</div>
              <div class="mt-8 text-13px leading-6 text-[#52606d]">{{ item.desc }}</div>
            </div>
          </div>
        </NCard>
      </NGi>

      <NGi>
        <NCard :bordered="false" class="card-wrapper h-full">
          <div class="mb-16 text-18px font-600 text-[#102a43]">Structure Notes</div>
          <div class="grid gap-12 text-14px text-[#334e68]">
            <div class="rounded-16px bg-[#f8fafc] p-14">
              Frontend keeps the SoybeanAdmin shell, permissions, menus and tabs.
            </div>
            <div class="rounded-16px bg-[#f8fafc] p-14">
              AG Grid is reserved for purchase orders, sales orders and stock adjustment sheets.
            </div>
            <div class="rounded-16px bg-[#f8fafc] p-14">
              Printable documents should use dedicated print views instead of printing the grid directly.
            </div>
          </div>
        </NCard>
      </NGi>
    </NGrid>
  </div>
</template>
