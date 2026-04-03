<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue';
import { NButton, NSpace, NTag } from 'naive-ui';
import {
  fetchAdminAccountLoginHistory,
  fetchAdminAccounts,
  resetAdminAccountPassword,
  updateAdminAccountStatus
} from '@/service/api';

const loading = ref(false);
const actionLoadingId = ref('');
const accounts = ref<Api.Company.AdminAccountItem[]>([]);
const passwordModalVisible = ref(false);
const passwordSubmitting = ref(false);
const selectedAccount = ref<Api.Company.AdminAccountItem | null>(null);
const passwordForm = reactive({ newPassword: '' });
const historyDrawerVisible = ref(false);
const historyLoading = ref(false);
const loginHistory = ref<Api.Company.AdminAccountLoginHistoryItem[]>([]);

const summary = computed(() => {
  const total = accounts.value.length;
  const platform = accounts.value.filter(item => item.accountType === 'platform').length;
  const companyAdmins = accounts.value.filter(item => item.accountType === 'company_admin').length;

  return { total, platform, companyAdmins };
});

const columns = computed(() => [
  { title: '姓名', key: 'fullName' },
  { title: '邮箱', key: 'email' },
  { title: '账号类型', key: 'accountType', render: accountTypeCell },
  { title: '所属公司', key: 'tenantName', render: textCell('tenantName') },
  { title: '租户角色', key: 'tenantRole', render: textCell('tenantRole') },
  { title: '状态', key: 'isActive', render: statusCell },
  { title: '操作', key: 'actions', render: actionCell }
]);

function textCell(key: keyof Api.Company.AdminAccountItem) {
  return (row: Api.Company.AdminAccountItem) => row[key] || '—';
}

function accountTypeCell(row: Api.Company.AdminAccountItem) {
  const isPlatform = row.accountType === 'platform';
  return h(
    NTag,
    { type: isPlatform ? 'primary' : 'info', round: true },
    { default: () => (isPlatform ? '平台账号' : '公司管理员') }
  );
}

function statusCell(row: Api.Company.AdminAccountItem) {
  return h(
    NTag,
    { type: row.isActive ? 'success' : 'warning', round: true },
    { default: () => (row.isActive ? '启用' : '停用') }
  );
}

function actionCell(row: Api.Company.AdminAccountItem) {
  return h(
    NSpace,
    { size: 8 },
    {
      default: () => [
        h(
          NButton,
          {
            size: 'small',
            secondary: true,
            type: row.isActive ? 'warning' : 'success',
            loading: actionLoadingId.value === row.id,
            onClick: () => handleToggleStatus(row)
          },
          { default: () => (row.isActive ? '停用' : '启用') }
        ),
        h(
          NButton,
          {
            size: 'small',
            quaternary: true,
            type: 'primary',
            onClick: () => openLoginHistory(row)
          },
          { default: () => '登录记录' }
        ),
        h(
          NButton,
          {
            size: 'small',
            quaternary: true,
            type: 'primary',
            onClick: () => openResetPassword(row)
          },
          { default: () => '重置密码' }
        )
      ]
    }
  );
}

async function loadAccounts() {
  loading.value = true;
  const { data, error } = await fetchAdminAccounts();
  if (!error && data) {
    accounts.value = data;
  }
  loading.value = false;
}

async function handleToggleStatus(row: Api.Company.AdminAccountItem) {
  actionLoadingId.value = row.id;
  const { data, error } = await updateAdminAccountStatus(row.id, !row.isActive);

  if (!error && data) {
    accounts.value = accounts.value.map(item => (item.id === row.id ? data : item));
    window.$message?.success(data.isActive ? '账号已启用' : '账号已停用');
  }

  actionLoadingId.value = '';
}

function openResetPassword(row: Api.Company.AdminAccountItem) {
  selectedAccount.value = row;
  passwordForm.newPassword = '';
  passwordModalVisible.value = true;
}

async function openLoginHistory(row: Api.Company.AdminAccountItem) {
  selectedAccount.value = row;
  historyDrawerVisible.value = true;
  historyLoading.value = true;
  loginHistory.value = [];

  const { data, error } = await fetchAdminAccountLoginHistory(row.id);
  if (!error && data) {
    loginHistory.value = data;
  }

  historyLoading.value = false;
}

async function submitResetPassword() {
  if (!selectedAccount.value || !passwordForm.newPassword) {
    return;
  }

  passwordSubmitting.value = true;
  const { error } = await resetAdminAccountPassword(selectedAccount.value.id, {
    newPassword: passwordForm.newPassword
  });

  if (!error) {
    passwordModalVisible.value = false;
    window.$message?.success('密码已重置');
  }

  passwordSubmitting.value = false;
}

onMounted(async () => {
  await loadAccounts();
});
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper">
      <div class="mb-16 flex flex-col gap-10 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div class="text-22px font-700 text-[#102a43]">账号管理</div>
          <div class="mt-6 text-13px text-[#52606d]">查看平台账号和公司管理员账号，支持启停和重置密码。</div>
        </div>
        <div class="flex flex-wrap gap-8 text-12px text-[#52606d]">
          <span class="rounded-999px bg-[#f1f5f9] px-10 py-4">全部 {{ summary.total }}</span>
          <span class="rounded-999px bg-[#eef4ff] px-10 py-4 text-[#1d4ed8]">平台 {{ summary.platform }}</span>
          <span class="rounded-999px bg-[#ecfeff] px-10 py-4 text-[#0f766e]">公司管理员 {{ summary.companyAdmins }}</span>
        </div>
      </div>

      <NDataTable
        :columns="columns"
        :data="accounts"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        size="small"
      />
    </NCard>

    <NModal
      v-model:show="passwordModalVisible"
      preset="card"
      title="重置密码"
      class="w-520px max-w-[94vw]"
      :bordered="false"
    >
      <NForm label-placement="top">
        <NFormItem label="新密码">
          <NInput
            v-model:value="passwordForm.newPassword"
            type="password"
            show-password-on="click"
            placeholder="请输入 8 位以上新密码"
          />
        </NFormItem>
      </NForm>

      <template #footer>
        <div class="flex justify-end gap-12">
          <NButton @click="passwordModalVisible = false">取消</NButton>
          <NButton type="primary" :loading="passwordSubmitting" @click="submitResetPassword">确认重置</NButton>
        </div>
      </template>
    </NModal>

    <NDrawer v-model:show="historyDrawerVisible" :width="520">
      <NDrawerContent :title="selectedAccount ? `${selectedAccount.fullName} 最近 7 次登录` : '最近 7 次登录'" closable>
        <template v-if="historyLoading">
          <NSkeleton text :repeat="7" />
        </template>

        <template v-else>
          <div class="grid gap-12">
            <div
              v-for="item in loginHistory"
              :key="item.id"
              class="rounded-12px bg-[#f8fafc] p-14"
            >
              <div class="text-12px text-[#7b8794]">登录时间</div>
              <div class="mt-6 text-14px text-[#102a43]">{{ item.loginAt }}</div>
              <div class="mt-10 text-12px text-[#7b8794]">IP</div>
              <div class="mt-6 text-14px text-[#102a43]">{{ item.loginIp || '—' }}</div>
            </div>

            <NEmpty v-if="!loginHistory.length" description="暂无登录记录" />
          </div>
        </template>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>
