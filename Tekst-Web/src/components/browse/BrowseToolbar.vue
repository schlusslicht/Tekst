<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { NButton, NBadge, NIcon, NFlex, useThemeVars } from 'naive-ui';
import BrowseLocationControls from '@/components/browse/BrowseLocationControls.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import { useBrowseStore, useStateStore } from '@/stores';

import { CompressIcon, ExpandIcon, ResourceIcon } from '@/icons';

const state = useStateStore();
const browse = useBrowseStore();
const themeVars = useThemeVars();

const affixRef = ref(null);
const resourcesCount = computed(
  () => browse.resourcesCategorized.map((c) => c.resources).flat().length
);
const activeResourcesCount = computed(
  () =>
    browse.resourcesCategorized
      .map((c) => c.resources)
      .flat()
      .filter((r) => r.active).length
);
const resourceDrawerBadgeLabel = computed(() =>
  resourcesCount.value ? activeResourcesCount.value + '/' + resourcesCount.value : '...'
);

onMounted(() => {
  if (affixRef.value) {
    new IntersectionObserver(
      ([e]) => e.target.classList.toggle('affixed', e.intersectionRatio < 1),
      { threshold: [1] }
    ).observe(affixRef.value);
  }
});

const buttonSize = computed(() => (state.smallScreen ? 'small' : 'large'));
</script>

<template>
  <div ref="affixRef" class="browse-toolbar-container accent-color-bg mb-lg">
    <n-flex
      v-show="!!state.text"
      :wrap="false"
      justify="space-around"
      align="center"
      class="browse-toolbar"
    >
      <browse-location-controls :button-size="buttonSize" />

      <div class="browse-toolbar-middle">
        <div
          v-show="!state.smallScreen"
          class="browse-location-label"
          :style="{ color: themeVars.bodyColor }"
        >
          <location-label />
        </div>
      </div>

      <div class="browse-toolbar-end">
        <n-badge value="!" color="var(--accent-color-pastel)" :show="browse.reducedView">
          <n-button
            type="primary"
            :size="buttonSize"
            :title="$t('browse.toolbar.tipReducedView')"
            :focusable="false"
            :color="browse.reducedView ? themeVars.primaryColorHover : undefined"
            @click="browse.reducedView = !browse.reducedView"
          >
            <template #icon>
              <n-icon :component="browse.reducedView ? ExpandIcon : CompressIcon" />
            </template>
          </n-button>
        </n-badge>

        <n-badge :value="resourceDrawerBadgeLabel" color="var(--accent-color-pastel)">
          <n-button
            type="primary"
            :size="buttonSize"
            :title="$t('browse.toolbar.tipOpenResourceList')"
            :focusable="false"
            @click="browse.showResourceToggleDrawer = true"
          >
            <template #icon>
              <n-icon :component="ResourceIcon" />
            </template>
          </n-button>
        </n-badge>
      </div>
    </n-flex>
  </div>
</template>

<style scoped>
.browse-toolbar-container {
  position: sticky;
  top: -1px;
  border-radius: var(--border-radius);
  box-shadow: var(--block-box-shadow);
  width: 100%;
  max-width: var(--max-app-width);
  padding: var(--gap-sm) 0;
  border-radius: var(--border-radius);
  box-shadow: var(--block-box-shadow);
  transition: none;
}

.browse-toolbar-container.affixed {
  border-top-left-radius: unset;
  border-top-right-radius: unset;
  max-width: unset;
  /* width: 100vw; */
  left: 0px;
  box-shadow: var(--fixed-box-shadow);
  z-index: 1801;
}

.browse-toolbar {
  margin: 0 var(--gap-sm);
}

.browse-toolbar-middle {
  flex-grow: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

.browse-toolbar-end {
  display: flex;
  gap: 12px;
}

.browse-toolbar-container.affixed .browse-toolbar {
  max-width: var(--max-app-width);
}

.browse-toolbar .browse-location-label {
  display: none;
}

.browse-toolbar-container.affixed .browse-location-label {
  display: initial;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

<style>
.browse-toolbar .n-badge > .n-badge-sup {
  color: var(--accent-color-dark);
}
</style>
