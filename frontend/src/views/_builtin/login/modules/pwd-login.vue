<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { Crypto } from '@sa/utils';
import { useAuthStore } from '@/store/modules/auth';
import { useRouterPush } from '@/hooks/common/router';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { localStg } from '@/utils/storage';

defineOptions({
  name: 'PwdLogin'
});

const authStore = useAuthStore();
const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useNaiveForm();

interface FormModel {
  email: string;
  password: string;
}

interface RememberedLogin {
  email: string;
  password: string;
  rememberMe: boolean;
}

const rememberedLoginCrypto = new Crypto<RememberedLogin>('fele-remember-login');

const model: FormModel = reactive({
  email: '',
  password: ''
});
const rememberMe = ref(false);

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => {
  const { formRules } = useFormRules();

  return {
    email: formRules.email,
    password: formRules.pwd
  };
});

async function handleSubmit() {
  await validate();
  persistRememberedLogin();
  await authStore.login(model.email, model.password);
}

function loadRememberedLogin() {
  const encrypted = localStg.get('rememberedLogin');

  if (!encrypted) {
    return;
  }

  const remembered = rememberedLoginCrypto.decrypt(encrypted);

  if (!remembered?.rememberMe) {
    localStg.remove('rememberedLogin');
    return;
  }

  model.email = remembered.email || '';
  model.password = remembered.password || '';
  rememberMe.value = true;
}

function persistRememberedLogin() {
  if (!rememberMe.value) {
    localStg.remove('rememberedLogin');
    return;
  }

  const encrypted = rememberedLoginCrypto.encrypt({
    email: model.email,
    password: model.password,
    rememberMe: true
  });

  localStg.set('rememberedLogin', encrypted);
}

onMounted(() => {
  loadRememberedLogin();
});
</script>

<template>
  <NForm ref="formRef" :model="model" :rules="rules" size="large" :show-label="false" @keyup.enter="handleSubmit">
    <NFormItem path="email">
      <NInput v-model:value="model.email" :placeholder="$t('page.login.common.emailPlaceholder')">
        <template #prefix>
          <icon-mdi-email-outline class="text-[#7b8794]" />
        </template>
      </NInput>
    </NFormItem>
    <NFormItem path="password">
      <NInput
        v-model:value="model.password"
        type="password"
        show-password-on="click"
        :placeholder="$t('page.login.common.passwordPlaceholder')"
      >
        <template #prefix>
          <icon-mdi-lock-outline class="text-[#7b8794]" />
        </template>
      </NInput>
    </NFormItem>
    <NSpace vertical :size="18">
      <NCheckbox v-model:checked="rememberMe">{{ $t('page.login.pwdLogin.rememberMe') }}</NCheckbox>
      <NButton type="primary" size="large" round block :loading="authStore.loginLoading" @click="handleSubmit">
        {{ $t('page.login.pwdLogin.signInNow') }}
      </NButton>
      <div class="flex-y-center justify-between gap-12px">
        <NButton class="flex-1" block @click="toggleLoginModule('register')">
          {{ $t('page.login.pwdLogin.register') }}
        </NButton>
        <NButton class="flex-1" block @click="toggleLoginModule('reset-pwd')">
          {{ $t('page.login.pwdLogin.forgetPassword') }}
        </NButton>
      </div>
    </NSpace>
  </NForm>
</template>

<style scoped></style>
