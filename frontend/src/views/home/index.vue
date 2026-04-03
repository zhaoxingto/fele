<script setup lang="ts">
const milestones = [
  'FastAPI backend scaffolded for multi-tenant SaaS inventory flows.',
  'Vue 3 + SoybeanAdmin shell added for navigation, tabs and theme management.',
  'AG Grid reserved for purchase, sales and stock sheet-style data entry.',
  'Document printing should be implemented as dedicated print templates.'
];
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper overflow-hidden">
      <div class="grid gap-20 lg:grid-cols-[1.2fr_0.8fr]">
        <div class="flex-col gap-12">
          <div class="text-12px uppercase tracking-[0.22em] text-[#0f766e]">Fele ERP</div>
          <div class="max-w-760px text-4xl font-700 leading-tight text-[#102a43]">
            Vue 3 management shell for a flexible SaaS inventory platform
          </div>
          <div class="max-w-680px text-15px leading-7 text-[#52606d]">
            This workspace is now aligned around SoybeanAdmin for the application shell and AG Grid for Excel-like line
            item entry in purchase, sales and warehouse documents.
          </div>
        </div>
        <div class="rounded-20px bg-[#f3fbf9] p-18">
          <div class="text-13px uppercase tracking-[0.16em] text-[#486581]">Current Stack</div>
          <div class="mt-14 grid gap-10 text-14px text-[#102a43]">
            <div class="rounded-14px bg-white p-12">Frontend: Vue 3, Vite, TypeScript, Pinia</div>
            <div class="rounded-14px bg-white p-12">Admin Shell: SoybeanAdmin + Naive UI + UnoCSS</div>
            <div class="rounded-14px bg-white p-12">Data Grid: AG Grid Community</div>
            <div class="rounded-14px bg-white p-12">Backend: FastAPI + SQLAlchemy 2.x</div>
          </div>
        </div>
      </div>
    </NCard>

    <NCard :bordered="false" class="card-wrapper">
      <div class="mb-16 text-18px font-600 text-[#102a43]">Project Milestones</div>
      <div class="grid gap-12">
        <div v-for="item in milestones" :key="item" class="rounded-16px bg-[#f8fafc] p-14 text-14px text-[#334e68]">
          {{ item }}
        </div>
      </div>
    </NCard>
  </div>
</template>
