<script setup lang="ts">
import { computed } from 'vue';
import type { Component } from 'vue';
import { getPaletteColorByNumber, mixColor } from '@sa/color';
import { loginModuleRecord } from '@/constants/app';
import { useAppStore } from '@/store/modules/app';
import { useThemeStore } from '@/store/modules/theme';
import { $t } from '@/locales';
import PwdLogin from './modules/pwd-login.vue';
import CodeLogin from './modules/code-login.vue';
import Register from './modules/register.vue';
import ResetPwd from './modules/reset-pwd.vue';
import BindWechat from './modules/bind-wechat.vue';

interface Props {
  /** The login module */
  module?: UnionKey.LoginModule;
}

const props = defineProps<Props>();

const appStore = useAppStore();
const themeStore = useThemeStore();

interface LoginModule {
  label: App.I18n.I18nKey;
  component: Component;
}

const moduleMap: Record<UnionKey.LoginModule, LoginModule> = {
  'pwd-login': { label: loginModuleRecord['pwd-login'], component: PwdLogin },
  'code-login': { label: loginModuleRecord['code-login'], component: CodeLogin },
  register: { label: loginModuleRecord.register, component: Register },
  'reset-pwd': { label: loginModuleRecord['reset-pwd'], component: ResetPwd },
  'bind-wechat': { label: loginModuleRecord['bind-wechat'], component: BindWechat }
};

const activeModule = computed(() => moduleMap[props.module || 'pwd-login']);

const bgThemeColor = computed(() =>
  themeStore.darkMode ? getPaletteColorByNumber(themeStore.themeColor, 600) : themeStore.themeColor
);

const bgColor = computed(() => {
  const COLOR_WHITE = '#ffffff';

  const ratio = themeStore.darkMode ? 0.5 : 0.2;

  return mixColor(COLOR_WHITE, themeStore.themeColor, ratio);
});

</script>

<template>
  <div class="relative h-screen min-h-screen overflow-hidden" :style="{ backgroundColor: bgColor }">
    <WaveBg :theme-color="bgThemeColor" />
    <div class="relative z-4 mx-auto flex h-full w-full max-w-7xl items-center justify-center px-6 py-4 sm:px-8">
      <NCard
        :bordered="false"
        class="w-full max-w-520px rounded-24px bg-white/92 px-3 py-2 shadow-[0_20px_64px_rgba(15,23,42,0.12)] backdrop-blur-xl"
      >
        <div class="mx-auto w-full max-w-420px lt-sm:max-w-none">
          <header class="flex items-start justify-between gap-12">
            <div class="flex items-center gap-12">
              <div class="flex-center size-50 rounded-16px bg-[#f3fbf9] text-[#0f766e]">
                <SystemLogo class="size-30px" />
              </div>
              <div>
                <div class="text-12px uppercase tracking-[0.2em] text-[#0f766e]">Fele ERP</div>
                <h3 class="mt-2 text-24px font-700 leading-tight text-[#102a43] lt-sm:text-22px">
                  {{ $t('system.title') }}
                </h3>
              </div>
            </div>
            <div class="i-flex-col gap-2">
              <ThemeSchemaSwitch
                :theme-schema="themeStore.themeScheme"
                :show-tooltip="false"
                class="text-20px lt-sm:text-18px"
                @switch="themeStore.toggleThemeScheme"
              />
              <LangSwitch
                v-if="themeStore.header.multilingual.visible"
                :lang="appStore.locale"
                :lang-options="appStore.localeOptions"
                :show-tooltip="false"
                @change-lang="appStore.changeLocale"
              />
            </div>
          </header>
          <main class="pt-5">
            <div class="text-13px leading-6 text-[#52606d]">
              使用公司管理员邮箱和密码登录，首次使用请先创建公司账号。
            </div>
            <h3 class="pt-4 text-18px font-600 text-[#102a43]">{{ $t(activeModule.label) }}</h3>
            <div class="pt-5">
              <Transition :name="themeStore.page.animateMode" mode="out-in" appear>
                <component :is="activeModule.component" />
              </Transition>
            </div>
          </main>
        </div>
      </NCard>
    </div>
  </div>
</template>

<style scoped></style>
