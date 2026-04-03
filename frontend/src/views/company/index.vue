<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue';
import { NButton, NSpace, NTag } from 'naive-ui';
import {
  createCategory,
  createCustomer,
  fetchCompanyCodeRules,
  createProduct,
  createSupplier,
  fetchCategories,
  fetchCompanyProfile,
  fetchCustomers,
  generateCompanyCode,
  fetchProducts,
  fetchSuppliers,
  updateCategory,
  updateCompanyCodeRules,
  updateCompanyProfile,
  updateCustomer,
  updateProduct,
  updateSupplier
} from '@/service/api';
import { useAuthStore } from '@/store/modules/auth';

type SectionKey = 'profile' | 'code_rules' | 'customers' | 'categories' | 'products' | 'suppliers';
type EditorMode = 'create' | 'edit';

const savingProfile = ref(false);
const savingCodeRules = ref(false);
const activeTab = ref<SectionKey>('profile');
const editorVisible = ref(false);
const editorMode = ref<EditorMode>('create');
const editorType = ref<SectionKey>('customers');
const editingId = ref('');
const submitting = ref(false);
const authStore = useAuthStore();
const hasTenant = computed(() => Boolean(authStore.userInfo.tenantId));

const profile = reactive<Api.Company.UpdateCompanyProfilePayload>({
  companyName: '',
  legalName: '',
  contactName: '',
  phone: '',
  email: '',
  address: '',
  remark: ''
});

const codeRules = reactive<Api.Company.CompanyCodeRules>({
  sku: {
    mode: 'date_random',
    prefix: 'SKU',
    digits: 4,
    nextNumber: 1
  },
  barcode: {
    mode: 'random',
    prefix: '69',
    digits: 10,
    nextNumber: 1
  }
});

const customers = ref<Api.Company.CustomerItem[]>([]);
const categories = ref<Api.Company.CategoryItem[]>([]);
const products = ref<Api.Company.ProductItem[]>([]);
const suppliers = ref<Api.Company.SupplierItem[]>([]);

const customerForm = reactive<Api.Company.CustomerPayload>({
  name: '',
  code: '',
  contactName: '',
  phone: '',
  email: '',
  address: '',
  remark: '',
  isActive: true
});

const categoryForm = reactive<Api.Company.CategoryPayload>({
  name: '',
  code: '',
  remark: '',
  isActive: true
});

const productForm = reactive<Api.Company.ProductPayload>({
  sku: '',
  barcode: '',
  name: '',
  categoryId: null,
  specification: '',
  unit: 'pcs',
  remark: '',
  isActive: true
});

const supplierForm = reactive<Api.Company.SupplierPayload>({
  name: '',
  code: '',
  contactName: '',
  phone: '',
  email: '',
  address: '',
  remark: '',
  isActive: true
});

const categoryOptions = computed(() =>
  categories.value.map(item => ({
    label: item.name,
    value: item.id
  }))
);

const dataStats = computed(() => [
  `客户 ${customers.value.length}`,
  `类别 ${categories.value.length}`,
  `产品 ${products.value.length}`,
  `供应商 ${suppliers.value.length}`
]);

const columnsBySection = computed<Record<SectionKey, any[]>>(() => ({
  profile: [],
  code_rules: [],
  customers: [
    { title: '客户名称', key: 'name' },
    { title: '客户编码', key: 'code', render: rowText('code') },
    { title: '联系人', key: 'contactName', render: rowText('contactName') },
    { title: '电话', key: 'phone', render: rowText('phone') },
    { title: '状态', key: 'isActive', render: rowStatus },
    { title: '操作', key: 'actions', render: rowAction('customers') }
  ],
  categories: [
    { title: '类别名称', key: 'name' },
    { title: '类别编码', key: 'code', render: rowText('code') },
    { title: '备注', key: 'remark', render: rowText('remark') },
    { title: '状态', key: 'isActive', render: rowStatus },
    { title: '操作', key: 'actions', render: rowAction('categories') }
  ],
  products: [
    { title: '产品名称', key: 'name' },
    { title: 'SKU', key: 'sku' },
    { title: '条码', key: 'barcode', render: rowText('barcode') },
    { title: '类别', key: 'categoryName', render: rowText('categoryName') },
    { title: '规格', key: 'specification', render: rowText('specification') },
    { title: '单位', key: 'unit' },
    { title: '状态', key: 'isActive', render: rowStatus },
    { title: '操作', key: 'actions', render: rowAction('products') }
  ],
  suppliers: [
    { title: '供应商名称', key: 'name' },
    { title: '供应商编码', key: 'code', render: rowText('code') },
    { title: '联系人', key: 'contactName', render: rowText('contactName') },
    { title: '电话', key: 'phone', render: rowText('phone') },
    { title: '状态', key: 'isActive', render: rowStatus },
    { title: '操作', key: 'actions', render: rowAction('suppliers') }
  ]
}));

const rowsBySection = computed<Record<SectionKey, any[]>>(() => ({
  profile: [],
  code_rules: [],
  customers: customers.value,
  categories: categories.value,
  products: products.value,
  suppliers: suppliers.value
}));

const sectionMeta: Record<SectionKey, { title: string; desc: string; action: string }> = {
  profile: {
    title: '公司基本信息',
    desc: '维护企业档案，后续子账号、单据抬头和对外资料都可以复用。',
    action: ''
  },
  code_rules: {
    title: '编码规则',
    desc: '设置 SKU 和条码的生成前缀、位数与起始序号。',
    action: ''
  },
  customers: {
    title: '客户档案',
    desc: '先把客户主数据沉淀下来，后续订单和对账都直接复用。',
    action: '新增客户'
  },
  categories: {
    title: '产品类别',
    desc: '先用一级类别建立统一口径，后面可以继续扩成多级分类。',
    action: '新增类别'
  },
  products: {
    title: '产品资料',
    desc: '把 SKU、规格、单位、所属类别先管起来，库存和订单才能稳定。',
    action: '新增产品'
  },
  suppliers: {
    title: '供应商档案',
    desc: '统一管理供应商基础信息，方便采购、到货和账期协同。',
    action: '新增供应商'
  }
};

function rowText(key: string) {
  return (row: Record<string, string | null | undefined>) => row[key] || '—';
}

function rowStatus(row: { isActive: boolean }) {
  return h(
    NTag,
    {
      type: row.isActive ? 'success' : 'warning',
      round: true
    },
    { default: () => (row.isActive ? '启用' : '停用') }
  );
}

function rowAction(type: SectionKey) {
  return (row: any) =>
    h(
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
              onClick: () => openEditor(type, 'edit', row)
            },
            { default: () => '编辑' }
          )
        ]
      }
    );
}

function resetProfile(profileData?: Api.Company.CompanyProfile) {
  profile.companyName = profileData?.companyName || '';
  profile.legalName = profileData?.legalName || '';
  profile.contactName = profileData?.contactName || '';
  profile.phone = profileData?.phone || '';
  profile.email = profileData?.email || '';
  profile.address = profileData?.address || '';
  profile.remark = profileData?.remark || '';
}

function resetCodeRules(data?: Api.Company.CompanyCodeRules) {
  codeRules.sku.mode = data?.sku.mode || 'date_random';
  codeRules.sku.prefix = data?.sku.prefix || '';
  codeRules.sku.digits = data?.sku.digits || 4;
  codeRules.sku.nextNumber = data?.sku.nextNumber || 1;
  codeRules.barcode.mode = data?.barcode.mode || 'random';
  codeRules.barcode.prefix = data?.barcode.prefix || '';
  codeRules.barcode.digits = data?.barcode.digits || 10;
  codeRules.barcode.nextNumber = data?.barcode.nextNumber || 1;
}

function resetEditorForm(type: SectionKey) {
  if (type === 'customers') {
    Object.assign(customerForm, {
      name: '',
      code: '',
      contactName: '',
      phone: '',
      email: '',
      address: '',
      remark: '',
      isActive: true
    });
    return;
  }

  if (type === 'categories') {
    Object.assign(categoryForm, {
      name: '',
      code: '',
      remark: '',
      isActive: true
    });
    return;
  }

  if (type === 'products') {
    Object.assign(productForm, {
      sku: '',
      barcode: '',
      name: '',
      categoryId: null,
      specification: '',
      unit: 'pcs',
      remark: '',
      isActive: true
    });
    return;
  }

  Object.assign(supplierForm, {
    name: '',
    code: '',
    contactName: '',
    phone: '',
    email: '',
    address: '',
    remark: '',
    isActive: true
  });
}

function openEditor(type: SectionKey, mode: EditorMode, row?: any) {
  editorType.value = type;
  editorMode.value = mode;
  editingId.value = row?.id || '';
  resetEditorForm(type);

  if (mode === 'edit' && row) {
    if (type === 'customers') {
      Object.assign(customerForm, row);
    } else if (type === 'categories') {
      Object.assign(categoryForm, row);
    } else if (type === 'products') {
      Object.assign(productForm, row);
    } else {
      Object.assign(supplierForm, row);
    }
  }

  editorVisible.value = true;
}

async function loadAll() {
  if (!hasTenant.value) {
    return;
  }

  const [
    profileRes,
    codeRulesRes,
    customersRes,
    categoriesRes,
    productsRes,
    suppliersRes
  ] = await Promise.all([
    fetchCompanyProfile(),
    fetchCompanyCodeRules(),
    fetchCustomers(),
    fetchCategories(),
    fetchProducts(),
    fetchSuppliers()
  ]);

  if (!profileRes.error && profileRes.data) {
    resetProfile(profileRes.data);
  }

  if (!codeRulesRes.error && codeRulesRes.data) {
    resetCodeRules(codeRulesRes.data);
  }

  if (!customersRes.error && customersRes.data) {
    customers.value = customersRes.data;
  }

  if (!categoriesRes.error && categoriesRes.data) {
    categories.value = categoriesRes.data;
  }

  if (!productsRes.error && productsRes.data) {
    products.value = productsRes.data;
  }

  if (!suppliersRes.error && suppliersRes.data) {
    suppliers.value = suppliersRes.data;
  }
}

async function submitProfile() {
  if (!hasTenant.value) {
    return;
  }

  savingProfile.value = true;
  const { data, error } = await updateCompanyProfile(profile);

  if (!error && data) {
    resetProfile(data);
    window.$message?.success('公司资料已保存');
  }

  savingProfile.value = false;
}

async function submitCodeRules() {
  if (!hasTenant.value) {
    return;
  }

  savingCodeRules.value = true;
  const { data, error } = await updateCompanyCodeRules(codeRules);

  if (!error && data) {
    resetCodeRules(data);
    window.$message?.success('编码规则已保存');
  }

  savingCodeRules.value = false;
}

async function handleGenerateCode(kind: 'sku' | 'barcode') {
  if (!hasTenant.value) {
    return;
  }

  const { data, error } = await generateCompanyCode({ kind });

  if (error || !data) {
    return;
  }

  if (kind === 'sku') {
    productForm.sku = data.code;
    codeRules.sku.nextNumber = data.nextNumber;
  } else {
    productForm.barcode = data.code;
    codeRules.barcode.nextNumber = data.nextNumber;
  }
}

async function submitEditor() {
  if (!hasTenant.value) {
    return;
  }

  submitting.value = true;

  const currentType = editorType.value;
  const isEdit = editorMode.value === 'edit';
  let result: { error: any; data?: any } | null = null;

  if (currentType === 'customers') {
    result = isEdit ? await updateCustomer(editingId.value, customerForm) : await createCustomer(customerForm);
  } else if (currentType === 'categories') {
    result = isEdit ? await updateCategory(editingId.value, categoryForm) : await createCategory(categoryForm);
  } else if (currentType === 'products') {
    result = isEdit ? await updateProduct(editingId.value, productForm) : await createProduct(productForm);
  } else {
    result = isEdit ? await updateSupplier(editingId.value, supplierForm) : await createSupplier(supplierForm);
  }

  if (!result?.error) {
    window.$message?.success(isEdit ? '资料已更新' : '资料已创建');
    editorVisible.value = false;
    await loadAll();
  }

  submitting.value = false;
}

const editorTitle = computed(() => `${editorMode.value === 'edit' ? '编辑' : '新增'}${sectionMeta[editorType.value].title}`);

onMounted(async () => {
  await loadAll();
});
</script>

<template>
  <div class="flex-col gap-16">
    <NCard :bordered="false" class="card-wrapper">
      <div class="mb-16 flex flex-col gap-10 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div class="text-22px font-700 text-[#102a43]">公司管理配置</div>
          <div class="mt-4 text-13px text-[#52606d]">维护公司基本信息、客户、产品类别、产品和供应商资料。</div>
        </div>
        <div class="flex flex-wrap gap-8 text-12px text-[#52606d]">
          <span
            v-for="item in dataStats"
            :key="item"
            class="rounded-999px bg-[#f1f5f9] px-10 py-4"
          >
            {{ item }}
          </span>
        </div>
      </div>

      <NTabs v-model:value="activeTab" type="line" animated>
        <NTabPane
          v-for="(meta, key) in sectionMeta"
          :key="key"
          :name="key"
          :tab="meta.title"
        >
          <template v-if="!hasTenant">
            <NAlert type="warning" :show-icon="false">
              当前登录账号没有绑定公司，暂时不能维护公司资料。请使用公司管理员账号登录，例如
              <span class="mx-4px font-600">owner@acme.local</span>
              ，或先把当前账号加入某个公司。
            </NAlert>
          </template>

          <template v-else-if="key === 'profile'">
            <div class="mb-16 text-13px text-[#52606d]">{{ meta.desc }}</div>

            <NForm label-placement="top">
              <NGrid cols="1 m:2" :x-gap="16" :y-gap="2" responsive="screen">
                <NGi>
                  <NFormItem label="公司名称">
                    <NInput v-model:value="profile.companyName" placeholder="例如: 飞乐贸易有限公司" />
                  </NFormItem>
                </NGi>
                <NGi>
                  <NFormItem label="法定名称">
                    <NInput v-model:value="profile.legalName" placeholder="营业执照上的完整名称" />
                  </NFormItem>
                </NGi>
                <NGi>
                  <NFormItem label="联系人">
                    <NInput v-model:value="profile.contactName" placeholder="公司管理员或对接人" />
                  </NFormItem>
                </NGi>
                <NGi>
                  <NFormItem label="联系电话">
                    <NInput v-model:value="profile.phone" placeholder="手机号或座机" />
                  </NFormItem>
                </NGi>
                <NGi>
                  <NFormItem label="邮箱">
                    <NInput v-model:value="profile.email" placeholder="常用联系邮箱" />
                  </NFormItem>
                </NGi>
                <NGi>
                  <NFormItem label="地址">
                    <NInput v-model:value="profile.address" placeholder="公司地址" />
                  </NFormItem>
                </NGi>
                <NGi span="2">
                  <NFormItem label="备注">
                    <NInput
                      v-model:value="profile.remark"
                      type="textarea"
                      :autosize="{ minRows: 2, maxRows: 4 }"
                      placeholder="可记录开票信息、经营范围、内部说明等"
                    />
                  </NFormItem>
                </NGi>
              </NGrid>
            </NForm>

            <div class="mt-4 flex justify-end">
              <NButton type="primary" :loading="savingProfile" @click="submitProfile">保存公司资料</NButton>
            </div>
          </template>

          <template v-else-if="key === 'code_rules'">
            <div class="mb-16 text-13px text-[#52606d]">{{ meta.desc }}</div>

            <NGrid cols="1 m:2" :x-gap="16" responsive="screen">
              <NGi>
                <NCard :bordered="false" class="bg-[#f8fafc]">
                  <div class="mb-12 text-16px font-600 text-[#102a43]">SKU 规则</div>
                  <NForm label-placement="top">
                    <NFormItem label="生成模式">
                      <NSelect
                        v-model:value="codeRules.sku.mode"
                        :options="[
                          { label: '顺序号', value: 'sequence' },
                          { label: '随机', value: 'random' },
                          { label: '日期 + 随机', value: 'date_random' }
                        ]"
                      />
                    </NFormItem>
                    <NFormItem label="前缀">
                      <NInput v-model:value="codeRules.sku.prefix" placeholder="例如: SKU" />
                    </NFormItem>
                    <NFormItem :label="codeRules.sku.mode === 'sequence' ? '数字位数' : '随机位数'">
                      <NInputNumber v-model:value="codeRules.sku.digits" class="w-full" :min="1" :max="20" />
                    </NFormItem>
                    <NFormItem v-if="codeRules.sku.mode === 'sequence'" label="下一个序号">
                      <NInputNumber
                        v-model:value="codeRules.sku.nextNumber"
                        class="w-full"
                        :min="1"
                        :max="999999999"
                      />
                    </NFormItem>
                  </NForm>
                </NCard>
              </NGi>

              <NGi>
                <NCard :bordered="false" class="bg-[#f8fafc]">
                  <div class="mb-12 text-16px font-600 text-[#102a43]">条码 规则</div>
                  <NForm label-placement="top">
                    <NFormItem label="生成模式">
                      <NSelect
                        v-model:value="codeRules.barcode.mode"
                        :options="[
                          { label: '顺序号', value: 'sequence' },
                          { label: '随机数字', value: 'random' }
                        ]"
                      />
                    </NFormItem>
                    <NFormItem label="前缀">
                      <NInput v-model:value="codeRules.barcode.prefix" placeholder="例如: 69" />
                    </NFormItem>
                    <NFormItem :label="codeRules.barcode.mode === 'sequence' ? '数字位数' : '随机位数'">
                      <NInputNumber v-model:value="codeRules.barcode.digits" class="w-full" :min="1" :max="20" />
                    </NFormItem>
                    <NFormItem v-if="codeRules.barcode.mode === 'sequence'" label="下一个序号">
                      <NInputNumber
                        v-model:value="codeRules.barcode.nextNumber"
                        class="w-full"
                        :min="1"
                        :max="999999999"
                      />
                    </NFormItem>
                  </NForm>
                </NCard>
              </NGi>
            </NGrid>

            <div class="mt-4 flex justify-end">
              <NButton type="primary" :loading="savingCodeRules" @click="submitCodeRules">保存编码规则</NButton>
            </div>
          </template>

          <template v-else>
            <div class="mb-16 flex flex-col gap-12 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div class="text-18px font-700 text-[#102a43]">{{ meta.title }}</div>
                <div class="mt-6 text-13px text-[#52606d]">{{ meta.desc }}</div>
              </div>
              <NButton type="primary" @click="openEditor(key as SectionKey, 'create')">{{ meta.action }}</NButton>
            </div>

            <NDataTable
              :columns="columnsBySection[key as SectionKey]"
              :data="rowsBySection[key as SectionKey]"
              :bordered="false"
              :single-line="false"
              size="small"
            />
          </template>
        </NTabPane>
      </NTabs>
    </NCard>

    <NModal
      v-model:show="editorVisible"
      preset="card"
      :title="editorTitle"
      class="w-720px max-w-[94vw]"
      :bordered="false"
    >
      <NForm label-placement="top">
        <template v-if="editorType === 'customers'">
          <NGrid cols="1 m:2" :x-gap="16" responsive="screen">
            <NGi><NFormItem label="客户名称"><NInput v-model:value="customerForm.name" /></NFormItem></NGi>
            <NGi><NFormItem label="客户编码"><NInput v-model:value="customerForm.code" /></NFormItem></NGi>
            <NGi><NFormItem label="联系人"><NInput v-model:value="customerForm.contactName" /></NFormItem></NGi>
            <NGi><NFormItem label="电话"><NInput v-model:value="customerForm.phone" /></NFormItem></NGi>
            <NGi><NFormItem label="邮箱"><NInput v-model:value="customerForm.email" /></NFormItem></NGi>
            <NGi><NFormItem label="地址"><NInput v-model:value="customerForm.address" /></NFormItem></NGi>
            <NGi span="2"><NFormItem label="备注"><NInput v-model:value="customerForm.remark" type="textarea" /></NFormItem></NGi>
            <NGi><NFormItem label="状态"><NSwitch v-model:value="customerForm.isActive" /></NFormItem></NGi>
          </NGrid>
        </template>

        <template v-else-if="editorType === 'categories'">
          <NGrid cols="1 m:2" :x-gap="16" responsive="screen">
            <NGi><NFormItem label="类别名称"><NInput v-model:value="categoryForm.name" /></NFormItem></NGi>
            <NGi><NFormItem label="类别编码"><NInput v-model:value="categoryForm.code" /></NFormItem></NGi>
            <NGi span="2"><NFormItem label="备注"><NInput v-model:value="categoryForm.remark" type="textarea" /></NFormItem></NGi>
            <NGi><NFormItem label="状态"><NSwitch v-model:value="categoryForm.isActive" /></NFormItem></NGi>
          </NGrid>
        </template>

        <template v-else-if="editorType === 'products'">
          <NGrid cols="1 m:2" :x-gap="16" responsive="screen">
            <NGi>
              <NFormItem label="SKU">
                <div class="flex w-full items-center gap-8">
                  <NInput v-model:value="productForm.sku" />
                  <NButton quaternary circle size="small" @click="handleGenerateCode('sku')">
                    <template #icon>
                      <icon-mdi-refresh />
                    </template>
                  </NButton>
                </div>
              </NFormItem>
            </NGi>
            <NGi>
              <NFormItem label="条码">
                <div class="flex w-full items-center gap-8">
                  <NInput v-model:value="productForm.barcode" />
                  <NButton quaternary circle size="small" @click="handleGenerateCode('barcode')">
                    <template #icon>
                      <icon-mdi-refresh />
                    </template>
                  </NButton>
                </div>
              </NFormItem>
            </NGi>
            <NGi><NFormItem label="产品名称"><NInput v-model:value="productForm.name" /></NFormItem></NGi>
            <NGi>
              <NFormItem label="所属类别">
                <NSelect v-model:value="productForm.categoryId" :options="categoryOptions" clearable />
              </NFormItem>
            </NGi>
            <NGi><NFormItem label="规格"><NInput v-model:value="productForm.specification" /></NFormItem></NGi>
            <NGi><NFormItem label="单位"><NInput v-model:value="productForm.unit" /></NFormItem></NGi>
            <NGi><NFormItem label="状态"><NSwitch v-model:value="productForm.isActive" /></NFormItem></NGi>
            <NGi span="2"><NFormItem label="备注"><NInput v-model:value="productForm.remark" type="textarea" /></NFormItem></NGi>
          </NGrid>
        </template>

        <template v-else>
          <NGrid cols="1 m:2" :x-gap="16" responsive="screen">
            <NGi><NFormItem label="供应商名称"><NInput v-model:value="supplierForm.name" /></NFormItem></NGi>
            <NGi><NFormItem label="供应商编码"><NInput v-model:value="supplierForm.code" /></NFormItem></NGi>
            <NGi><NFormItem label="联系人"><NInput v-model:value="supplierForm.contactName" /></NFormItem></NGi>
            <NGi><NFormItem label="电话"><NInput v-model:value="supplierForm.phone" /></NFormItem></NGi>
            <NGi><NFormItem label="邮箱"><NInput v-model:value="supplierForm.email" /></NFormItem></NGi>
            <NGi><NFormItem label="地址"><NInput v-model:value="supplierForm.address" /></NFormItem></NGi>
            <NGi span="2"><NFormItem label="备注"><NInput v-model:value="supplierForm.remark" type="textarea" /></NFormItem></NGi>
            <NGi><NFormItem label="状态"><NSwitch v-model:value="supplierForm.isActive" /></NFormItem></NGi>
          </NGrid>
        </template>
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
