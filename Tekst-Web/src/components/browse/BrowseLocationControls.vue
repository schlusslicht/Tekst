<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore, useBrowseStore } from '@/stores';
import { NBadge, NButton, NIcon } from 'naive-ui';
import type { LocationRead } from '@/api';
import router from '@/router';
import { useMagicKeys, whenever } from '@vueuse/core';
import { $t } from '@/i18n';
import LocationSelectModal from '@/components/modals/LocationSelectModal.vue';
import BookmarksWidget from '@/components/browse/BookmarksWidget.vue';

import { ArrowBackIcon, ArrowForwardIcon, BookIcon } from '@/icons';
import { isInputFocused, isOverlayOpen } from '@/utils';

withDefaults(
  defineProps<{
    buttonSize?: 'small' | 'medium' | 'large';
  }>(),
  {
    buttonSize: 'large',
  }
);

const auth = useAuthStore();
const browse = useBrowseStore();
const route = useRoute();
const position = computed<number>(() => parseInt(route.query.pos?.toString() || '0'));

const { ArrowLeft, ArrowRight } = useMagicKeys();

const showLocationSelectModal = ref(false);

function getPrevNextRoute(step: number) {
  return {
    ...route,
    query: {
      ...route.query,
      pos: position.value >= 0 ? position.value + step : 0,
    },
  };
}

function handleLocationSelect(locationPath: LocationRead[]) {
  const selectedLocation = locationPath[locationPath.length - 1];
  if (!selectedLocation) return;
  router.push({
    name: 'browse',
    params: { ...route.params },
    query: {
      lvl: selectedLocation.level,
      pos: selectedLocation.position,
    },
  });
}

// react to keyboard for in-/decreasing location
whenever(ArrowLeft, () => {
  !isOverlayOpen() && !isInputFocused() && router.replace(getPrevNextRoute(-1));
});
whenever(ArrowRight, () => {
  !isOverlayOpen() && !isInputFocused() && router.replace(getPrevNextRoute(1));
});
</script>

<template>
  <!-- text location toolbar buttons -->
  <div class="text-location">
    <router-link
      v-slot="{
        // @ts-ignore
        navigate,
      }"
      :to="getPrevNextRoute(-1)"
      custom
    >
      <n-button
        type="primary"
        :disabled="browse.position === 0"
        :focusable="false"
        :title="$t('browse.toolbar.tipPreviousLocation')"
        :size="buttonSize"
        @click="navigate"
      >
        <template #icon>
          <n-icon :component="ArrowBackIcon" />
        </template>
      </n-button>
    </router-link>

    <n-badge value="!" color="var(--accent-color-pastel)" :show="!browse.isOnDefaultLevel">
      <n-button
        type="primary"
        :title="
          $t('browse.toolbar.tipSelectLocation') +
          (!browse.isOnDefaultLevel ? ' (' + $t('browse.toolbar.tipNotOnDefaultLevel') + ')' : '')
        "
        :focusable="false"
        :size="buttonSize"
        @click="showLocationSelectModal = true"
      >
        <template #icon>
          <n-icon :component="BookIcon" />
        </template>
      </n-button>
    </n-badge>

    <bookmarks-widget v-if="auth.loggedIn" :size="buttonSize" />

    <router-link v-slot="{ navigate }" :to="getPrevNextRoute(1)" custom>
      <n-button
        type="primary"
        :focusable="false"
        :title="$t('browse.toolbar.tipNextLocation')"
        :size="buttonSize"
        @click="navigate"
      >
        <template #icon>
          <n-icon :component="ArrowForwardIcon" />
        </template>
      </n-button>
    </router-link>
  </div>

  <location-select-modal
    v-model:show="showLocationSelectModal"
    :current-location-path="browse.locationPath"
    @submit="handleLocationSelect"
  />
</template>

<style scoped>
.text-location {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
</style>
