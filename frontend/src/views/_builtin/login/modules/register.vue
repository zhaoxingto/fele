<script setup lang="ts">
import { computed, reactive } from 'vue';
import { fetchRegisterCompany } from '@/service/api';
import { useRouterPush } from '@/hooks/common/router';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'Register'
});

const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useNaiveForm();

interface FormModel {
  companyName: string;
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const model: FormModel = reactive({
  companyName: '',
  fullName: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => {
  const { formRules, createConfirmPwdRule, createRequiredRule } = useFormRules();

  return {
    companyName: [createRequiredRule($t('page.login.register.companyNameRequired'))],
    fullName: [createRequiredRule($t('page.login.register.fullNameRequired'))],
    email: formRules.email,
    password: formRules.pwd,
    confirmPassword: createConfirmPwdRule(model.password)
  };
});

async function handleSubmit() {
  await validate();
  const { data, error } = await fetchRegisterCompany({
    company_name: model.companyName,
    full_name: model.fullName,
    email: model.email,
    password: model.password
  });

  if (!error) {
    window.$dialog?.success({
      title: $t('page.login.register.successTitle'),
      content: $t('page.login.register.successDesc', {
        companyName: data.companyName,
        companyId: data.companyId
      }),
      positiveText: $t('page.login.common.back'),
      onPositiveClick() {
        toggleLoginModule('pwd-login');
      }
    });
  }
}
</script>

<template>
  <NForm ref="formRef" :model="model" :rules="rules" size="large" :show-label="false" @keyup.enter="handleSubmit">
    <NFormItem path="companyName">
      <NInput v-model:value="model.companyName" :placeholder="$t('page.login.register.companyNamePlaceholder')" />
    </NFormItem>
    <NFormItem path="fullName">
      <NInput v-model:value="model.fullName" :placeholder="$t('page.login.register.fullNamePlaceholder')" />
    </NFormItem>
    <NFormItem path="email">
      <NInput v-model:value="model.email" :placeholder="$t('page.login.common.emailPlaceholder')" />
    </NFormItem>
    <NFormItem path="password">
      <NInput
        v-model:value="model.password"
        type="password"
        show-password-on="click"
        :placeholder="$t('page.login.common.passwordPlaceholder')"
      />
    </NFormItem>
    <NFormItem path="confirmPassword">
      <NInput
        v-model:value="model.confirmPassword"
        type="password"
        show-password-on="click"
        :placeholder="$t('page.login.common.confirmPasswordPlaceholder')"
      />
    </NFormItem>
    <NSpace vertical :size="18" class="w-full">
      <NButton type="primary" size="large" round block @click="handleSubmit">
        {{ $t('page.login.register.createCompany') }}
      </NButton>
      <NButton size="large" round block @click="toggleLoginModule('pwd-login')">
        {{ $t('page.login.common.back') }}
      </NButton>
    </NSpace>
  </NForm>
</template>

<style scoped></style>
