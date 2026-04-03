<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue';
import { NButton, NSpace, NTag } from 'naive-ui';
import { fetchAdminTenantDetail, fetchAdminTenants, updateAdminTenantStatus } from '@/service/api';

const loading = ref(false);
const actionLoadingId = ref('');
const tenants = ref<Api.Company.AdminTenantListItem[]>([]);
const detailVisible = ref(false);
const detailLoading = ref(false);
const detail = ref<Api.Company.AdminTenantDetail | null>(null);

const summary = computed(() => {
  const total = tenants.value.length;
  const active = tenants.value.filter(item => item.isActive).length;
  const inactive = total - active;

  return { total, active, inactive };
});

const columns = computed(() => [
  { title: '公司名称', key: 'companyName' },
  { title: '公司 ID', key: 'companyId' },
  { title: '租户 Schema', key: 'schemaName' },
  { title: '负责人', key: 'ownerName', render: textCell('ownerName') },
  { title: '负责人邮箱', key: 'ownerEmail', render: textCell('ownerEmail') },
  { title: '联系电话', key: 'phone', render: textCell('phone') },
  { title: '状态', key: 'isActive', render: statusCell },
  { title: '操作', key: 'actions', render: actionCell }
]);

function textCell(key: keyof Api.Company.AdminTenantListItem) {
  return (row: Api.Company.AdminTenantListItem) => row[key] || '—';
}

function statusCell(row: Api.Company.AdminTenantListItem) {
  return h(
    NTag,
    { type: row.isActive ? 'success' : 'warning', round: true },
    { default: () => (row.isActive ? '启用' : '停用') }
  );
}

function actionCell(row: Api.Company.AdminTenantListItem) {
  const nextActive = !row.isActive;

  return h(
    NSpace,
    { size: 8 },
    {
      default: () => [
        h(
          NButton,
          {
            size: 'small',
            quaternary: true,
            type: 'primary',
            onClick: () => openDetail(row.id)
          },
          { default: () => '查看' }
        ),
        h(
          NButton,
          {
            size: 'small',
            secondary: true,
            type: row.isActive ? 'warning' : 'success',
            loading: actionLoadingId.value === row.id,
            onClick: () => handleToggleStatus(row.id, nextActive)
          },
          { default: () => (row.isActive ? '停用' : '启用') }
        )
      ]
    }
  );
}

async function loadTenants() {
  loading.value = true;
  const { data, error } = await fetchAdminTenants();

  if (!error && data) {
    tenants.value = data;
  }

  loading.value = false;
}

async function openDetail(id: string) {
  detailVisible.value = true;
  detailLoading.value = true;
  detail.value = null;

  const { data, error } = await fetchAdminTenantDetail(id);

  if (!error && data) {
    detail.value = data;
  }

  detailLoading.value = false;
}

async function handleToggleStatus(id: string, isActive: boolean) {
  actionLoadingId.value = id;
  const { data, error } = await updateAdminTenantStatus(id, isActive);

  if (!error && data) {
    tenants.value = tenants.value.map(item => (item.id === id ? data : item));

    if (detail.value?.id === id) {
      detail.value = { ...detail.value, ...data };
    }

    window.$message?.success(isActive ? '公司已启用' : '公司已停用');
  }

  actionLoadingId.value = '';
}

onMounted(async () => {
  await loadTenants();
});
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper">
      <div class="mb-16 flex flex-col gap-10 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div class="text-22px font-700 text-[#102a43]">公司管理</div>
          <div class="mt-6 text-13px text-[#52606d]">查看全部公司、启停状态，以及每个租户的基础信息。</div>
        </div>
        <div class="flex flex-wrap gap-8 text-12px text-[#52606d]">
          <span class="rounded-999px bg-[#f1f5f9] px-10 py-4">全部 {{ summary.total }}</span>
          <span class="rounded-999px bg-[#ecfdf3] px-10 py-4 text-[#027a48]">启用 {{ summary.active }}</span>
          <span class="rounded-999px bg-[#fffaeb] px-10 py-4 text-[#b54708]">停用 {{ summary.inactive }}</span>
        </div>
      </div>

      <NDataTable
        :columns="columns"
        :data="tenants"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        size="small"
      />
    </NCard>

    <NDrawer v-model:show="detailVisible" :width="520">
      <NDrawerContent title="租户信息" closable>
        <template v-if="detailLoading">
          <NSkeleton text :repeat="8" />
        </template>

        <template v-else-if="detail">
          <div class="grid gap-12">
            <div class="rounded-12px bg-[#f8fafc] p-14">
              <div class="text-12px text-[#7b8794]">公司名称</div>
              <div class="mt-6 text-16px font-600 text-[#102a43]">{{ detail.companyName }}</div>
            </div>
            <div class="grid gap-12 md:grid-cols-2">
              <div class="rounded-12px bg-[#f8fafc] p-14">
                <div class="text-12px text-[#7b8794]">公司 ID</div>
                <div class="mt-6 text-14px text-[#102a43]">{{ detail.companyId }}</div>
              </div>
              <div class="rounded-12px bg-[#f8fafc] p-14">
                <div class="text-12px text-[#7b8794]">Schema</div>
                <div class="mt-6 text-14px text-[#102a43]">{{ detail.schemaName }}</div>
              </div>
              <div class="rounded-12px bg-[#f8fafc] p-14">
                <div class="text-12px text-[#7b8794]">负责人</div>
                <div class="mt-6 text-14px text-[#102a43]">{{ detail.ownerName || '—' }}</div>
              </div>
              <div class="rounded-12px bg-[#f8fafc] p-14">
                <div class="text-12px text-[#7b8794]">负责人邮箱</div>
                <div class="mt-6 text-14px text-[#102a43]">{{ detail.ownerEmail || '—' }}</div>
              </div>
              <div class="rounded-12px bg-[#f8fafc] p-14">
                <div class="text-12px text-[#7b8794]">联系人</div>
                <div class="mt-6 text-14px text-[#102a43]">{{ detail.contactName || '—' }}</div>
              </div>
              <div class="rounded-12px bg-[#f8fafc] p-14">
                <div class="text-12px text-[#7b8794]">联系电话</div>
                <div class="mt-6 text-14px text-[#102a43]">{{ detail.phone || '—' }}</div>
              </div>
              <div class="rounded-12px bg-[#f8fafc] p-14">
                <div class="text-12px text-[#7b8794]">邮箱</div>
                <div class="mt-6 text-14px text-[#102a43]">{{ detail.email || '—' }}</div>
              </div>
              <div class="rounded-12px bg-[#f8fafc] p-14">
                <div class="text-12px text-[#7b8794]">状态</div>
                <div class="mt-6">
                  <NTag :type="detail.isActive ? 'success' : 'warning'" round>
                    {{ detail.isActive ? '启用' : '停用' }}
                  </NTag>
                </div>
              </div>
            </div>
            <div class="rounded-12px bg-[#f8fafc] p-14">
              <div class="text-12px text-[#7b8794]">地址</div>
              <div class="mt-6 text-14px leading-6 text-[#102a43]">{{ detail.address || '—' }}</div>
            </div>
            <div class="rounded-12px bg-[#f8fafc] p-14">
              <div class="text-12px text-[#7b8794]">备注</div>
              <div class="mt-6 text-14px leading-6 text-[#102a43]">{{ detail.remark || '—' }}</div>
            </div>
          </div>
        </template>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>
