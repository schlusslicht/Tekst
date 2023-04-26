import { ref, computed, watch } from 'vue';
import { defineStore } from 'pinia';
import { useWindowSize } from '@vueuse/core';
import type { RouteLocationNormalized } from 'vue-router';
import { usePlatformStore } from '@/stores';
import { i18n, setI18nLocale } from '@/i18n';
import type { AvailableLocale } from '@/i18n';
import { useRoute } from 'vue-router';
import type { TextRead } from '@/openapi';
import type { ThemeMode } from '@/theme';
import { useI18n } from 'vue-i18n';

export const useStateStore = defineStore('state', () => {
  // define resources
  const pf = usePlatformStore();
  const route = useRoute();
  const windowSize = useWindowSize();
  const { t, te } = useI18n({ useScope: 'global' });

  // theme
  const themeMode = ref<ThemeMode>((localStorage.getItem('theme') as ThemeMode) || 'light');
  watch(themeMode, (after) => localStorage.setItem('theme', after));

  function toggleThemeMode() {
    themeMode.value = themeMode.value === 'light' ? 'dark' : 'light';
  }

  // locale
  const locale = ref(localStorage.getItem('locale') || i18n.global.locale);
  watch(locale, (after) => {
    localStorage.setItem('locale', after);
    setPageTitle();
  });
  const locales = i18n.global.availableLocales;
  async function setLocale(l: string = locale.value): Promise<AvailableLocale> {
    return setI18nLocale(l).then((lang: AvailableLocale) => {
      locale.value = lang.key;
      return lang;
    });
  }

  // current text
  const text = ref<TextRead>();
  watch(route, (after) => {
    if ('text' in after.params && after.params.text && text.value?.slug !== after.params.text) {
      // use text from route OR default text
      text.value =
        pf.data?.texts.find((t) => t.slug === after.params.text) ||
        pf.data?.texts.find((t) => t.id === pf.data?.settings.defaultTextId);
    }
  });
  watch(text, () => {
    setPageTitle(route);
    text.value && localStorage.setItem('text', text.value?.slug);
  });

  // fallback text for invalid text references
  const fallbackText = computed(
    () =>
      text.value ||
      pf.data?.texts.find((t) => t.slug == localStorage.getItem('text')) ||
      pf.data?.texts.find((t) => t.id === pf.data?.settings.defaultTextId) ||
      pf.data?.texts[0]
  );

  // global loading state
  const globalLoading = ref(false);
  const globalLoadingMsg = ref('');
  const globalLoadingProgress = ref(0);
  const startGlobalLoading = () => {
    globalLoading.value = true;
  };
  const finishGlobalLoading = async (delayMs: number = 0, resetLoadingDataDelayMs: number = 0) => {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    globalLoading.value = false;
    await new Promise((resolve) => setTimeout(resolve, resetLoadingDataDelayMs));
    globalLoadingMsg.value = '...';
    globalLoadingProgress.value = 0;
  };

  // small screen (< 860px)
  const smallScreen = computed(() => windowSize.width.value < 860);
  const dropdownSize = computed(() => (smallScreen.value ? 'huge' : undefined));

  // set page title
  function setPageTitle(forRoute?: RouteLocationNormalized) {
    const r = forRoute || route;
    const rTitle = te(`routes.pageTitle.${String(r.name)}`)
      ? t(`routes.pageTitle.${String(r.name)}`)
      : '';
    const tTitle = 'text' in r.params && text.value?.title && ` "${text.value?.title}"`;
    const pfName = pf.data?.info?.platformName ? ` | ${pf.data?.info?.platformName}` : '';
    document.title = `${rTitle || ''}${tTitle || ''}${pfName}`;
  }

  return {
    globalLoading,
    startGlobalLoading,
    finishGlobalLoading,
    globalLoadingMsg,
    globalLoadingProgress,
    smallScreen,
    dropdownSize,
    setPageTitle,
    themeMode,
    toggleThemeMode,
    locale,
    locales,
    text,
    fallbackText,
    setLocale,
  };
});
