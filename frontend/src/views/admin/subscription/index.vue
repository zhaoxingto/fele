<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue';
import { NButton, NTag } from 'naive-ui';
import { fetchAdminSubscriptions, updateAdminSubscription } from '@/service/api';

const loading = ref(false);
const subscriptions = ref<Api.Company.AdminSubscriptionItem[]>([]);
const editorVisible = ref(false);
const editingTenantId = ref('');
const submitting = ref(false);
const statusFilter = ref<string | null>(null);

const presetOptions = [
  { label: 'Basic', value: 'Basic', scope: 'users=5, warehouses=1, reports=basic' },
  { label: 'Professional', value: 'Professional', scope: 'users=20, warehouses=3, reports=all' },
  { label: 'Enterprise', value: 'Enterprise', scope: 'users=unlimited, warehouses=unlimited, reports=all, api=enabled' }
];

const form = reactive<Api.Company.AdminSubscriptionPayload>({
  subscriptionPlan: '',
  subscriptionStatus: '',
  subscriptionExpiresAt: '',
  subscriptionScope: ''
});

const filteredSubscriptions = computed(() => {
  if (!statusFilter.value) {
    return subscriptions.value;
  }

  return subscriptions.value.filter(item => item.subscriptionStatus === statusFilter.value);
});

const summary = computed(() => {
  const total = subscriptions.value.length;
  const active = subscriptions.value.filter(item => item.subscriptionStatus === 'active').length;
  const trial = subscriptions.value.filter(item => item.subscriptionStatus === 'trial').length;
  const expired = subscriptions.value.filter(item => item.subscriptionStatus === 'expired').length;
  const expiringSoon = subscriptions.value.filter(item => isExpiringSoon(item.subscriptionExpiresAt)).length;

  return { total, active, trial, expired, expiringSoon };
});

const columns = computed(() => [
  { title: '公司名称', key: 'companyName' },
  { title: '公司 ID', key: 'companyId' },
  { title: '套餐', key: 'subscriptionPlan', render: textCell('subscriptionPlan') },
  { title: '状态', key: 'subscriptionStatus', render: statusCell },
  { title: '到期时间', key: 'subscriptionExpiresAt', render: expiryCell },
  { title: '授权范围', key: 'subscriptionScope', render: textCell('subscriptionScope') },
  { title: '操作', key: 'actions', render: actionCell }
]);

function textCell(key: keyof Api.Company.AdminSubscriptionItem) {
  return (row: Api.Company.AdminSubscriptionItem) => row[key] || '—';
}

function statusCell(row: Api.Company.AdminSubscriptionItem) {
  const status = row.subscriptionStatus || 'unset';
  const typeMap: Record<string, 'default' | 'success' | 'info' | 'warning' | 'error'> = {
    active: 'success',
    trial: 'info',
    paused: 'warning',
    expired: 'error',
    unset: 'default'
  };

  return h(
    NTag,
    { type: typeMap[status] || 'default', round: true },
    { default: () => status }
  );
}

function expiryCell(row: Api.Company.AdminSubscriptionItem) {
  const value = row.subscriptionExpiresAt || '—';
  const soon = isExpiringSoon(row.subscriptionExpiresAt);

  if (!soon) {
    return value;
  }

  return h('div', { class: 'flex items-center gap-8' }, [
    h('span', value),
    h(
      NTag,
      { type: 'warning', round: true, size: 'small' as const },
      { default: () => '临期' }
    )
  ]);
}

function actionCell(row: Api.Company.AdminSubscriptionItem) {
  return h(
    NButton,
    {
      size: 'small',
      quaternary: true,
      type: 'primary',
      onClick: () => openEditor(row)
    },
    { default: () => '编辑' }
  );
}

function isExpiringSoon(value?: string | null) {
  if (!value) {
    return false;
  }

  const expiresAt = new Date(value).getTime();
  if (Number.isNaN(expiresAt)) {
    return false;
  }

  const diff = expiresAt - Date.now();
  const days = diff / (1000 * 60 * 60 * 24);
  return days >= 0 && days <= 30;
}

async function loadSubscriptions() {
  loading.value = true;
  const { data, error } = await fetchAdminSubscriptions();
  if (!error && data) {
    subscriptions.value = data;
  }
  loading.value = false;
}

function openEditor(row: Api.Company.AdminSubscriptionItem) {
  editingTenantId.value = row.tenantId;
  form.subscriptionPlan = row.subscriptionPlan || '';
  form.subscriptionStatus = row.subscriptionStatus || '';
  form.subscriptionExpiresAt = row.subscriptionExpiresAt || '';
  form.subscriptionScope = row.subscriptionScope || '';
  editorVisible.value = true;
}

function applyPreset(plan: string | null) {
  const preset = presetOptions.find(item => item.value === plan);
  if (!preset) {
    return;
  }

  form.subscriptionPlan = preset.value;
  if (!form.subscriptionScope) {
    form.subscriptionScope = preset.scope;
  }
}

async function submitEditor() {
  submitting.value = true;
  const payload: Api.Company.AdminSubscriptionPayload = {
    subscriptionPlan: form.subscriptionPlan || null,
    subscriptionStatus: form.subscriptionStatus || null,
    subscriptionExpiresAt: form.subscriptionExpiresAt || null,
    subscriptionScope: form.subscriptionScope || null
  };

  const { data, error } = await updateAdminSubscription(editingTenantId.value, payload);

  if (!error && data) {
    subscriptions.value = subscriptions.value.map(item => (item.tenantId === data.tenantId ? data : item));
    editorVisible.value = false;
    window.$message?.success('订阅信息已更新');
  }

  submitting.value = false;
}

onMounted(async () => {
  await loadSubscriptions();
});
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper">
      <div class="mb-16 flex flex-col gap-10 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div class="text-22px font-700 text-[#102a43]">订阅管理</div>
          <div class="mt-6 text-13px text-[#52606d]">支持按状态筛选、套餐预设和临期提醒。</div>
        </div>
        <div class="flex flex-wrap gap-8 text-12px text-[#52606d]">
          <span class="rounded-999px bg-[#f1f5f9] px-10 py-4">全部 {{ summary.total }}</span>
          <span class="rounded-999px bg-[#ecfdf3] px-10 py-4 text-[#027a48]">Active {{ summary.active }}</span>
          <span class="rounded-999px bg-[#eff6ff] px-10 py-4 text-[#1d4ed8]">Trial {{ summary.trial }}</span>
          <span class="rounded-999px bg-[#fff7ed] px-10 py-4 text-[#c2410c]">Expired {{ summary.expired }}</span>
          <span class="rounded-999px bg-[#fef3f2] px-10 py-4 text-[#b42318]">临期 {{ summary.expiringSoon }}</span>
        </div>
      </div>

      <div class="mb-16 flex flex-wrap gap-10">
        <NSelect
          v-model:value="statusFilter"
          class="w-220px"
          clearable
          placeholder="按状态筛选"
          :options="[
            { label: 'Trial', value: 'trial' },
            { label: 'Active', value: 'active' },
            { label: 'Paused', value: 'paused' },
            { label: 'Expired', value: 'expired' }
          ]"
        />
      </div>

      <NDataTable
        :columns="columns"
        :data="filteredSubscriptions"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        size="small"
      />
    </NCard>

    <NModal v-model:show="editorVisible" preset="card" title="编辑订阅" class="w-640px max-w-[94vw]" :bordered="false">
      <NForm label-placement="top">
        <NGrid cols="1 m:2" :x-gap="16" responsive="screen">
          <NGi>
            <NFormItem label="套餐">
              <NSelect
                v-model:value="form.subscriptionPlan"
                :options="presetOptions.map(item => ({ label: item.label, value: item.value }))"
                clearable
                @update:value="applyPreset"
              />
            </NFormItem>
          </NGi>
          <NGi>
            <NFormItem label="状态">
              <NSelect
                v-model:value="form.subscriptionStatus"
                :options="[
                  { label: 'Trial', value: 'trial' },
                  { label: 'Active', value: 'active' },
                  { label: 'Paused', value: 'paused' },
                  { label: 'Expired', value: 'expired' }
                ]"
                clearable
              />
            </NFormItem>
          </NGi>
          <NGi span="2">
            <NFormItem label="到期时间">
              <NInput
                v-model:value="form.subscriptionExpiresAt"
                placeholder="例如: 2026-12-31T23:59:59+08:00"
              />
            </NFormItem>
          </NGi>
          <NGi span="2">
            <NFormItem label="授权范围">
              <NInput
                v-model:value="form.subscriptionScope"
                type="textarea"
                :autosize="{ minRows: 3, maxRows: 5 }"
                placeholder="例如: users=20, warehouses=3, reports=all"
              />
            </NFormItem>
          </NGi>
        </NGrid>
      </NForm>

      <template #footer>
        <div class="flex justify-end gap-12">
          <NButton @click="editorVisible = false">取消</NButton>
          <NButton type="primary" :loading="submitting" @click="submitEditor">保存</NButton>
        </div>
      </template>
    </NModal>
  </div>
</template>
