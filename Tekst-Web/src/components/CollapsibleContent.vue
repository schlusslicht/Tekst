<script setup lang="ts">
import { CompressIcon, ExpandIcon } from '@/icons';
import { useElementSize } from '@vueuse/core';
import { NButton, NIcon } from 'naive-ui';
import { computed, ref } from 'vue';

const props = withDefaults(
  defineProps<{
    collapsible?: boolean;
    heightTreshPx?: number;
    collapseText?: string;
    expandText?: string;
    showBtnText?: boolean;
  }>(),
  {
    collapsible: true,
    heightTreshPx: 150,
    showBtnText: true,
  }
);

const contentRef = ref<HTMLElement>();
const { height } = useElementSize(contentRef);
const collapsed = defineModel<boolean>({ required: false, default: true });
const isCollapsible = computed(() => props.collapsible && height.value > props.heightTreshPx);
const isCollapsed = computed(() => isCollapsible.value && collapsed.value);
</script>

<template>
  <div>
    <div
      :class="{ collapsed: isCollapsed }"
      :style="{
        maxHeight: isCollapsed ? `${heightTreshPx}px` : undefined,
        overflow: 'hidden',
      }"
    >
      <div ref="contentRef">
        <slot></slot>
      </div>
      <div class="collapsed-shadow"></div>
    </div>
    <n-button
      v-if="isCollapsible"
      text
      block
      class="mt-sm"
      :focusable="false"
      :size="showBtnText ? undefined : 'large'"
      @click.stop.prevent="collapsed = !collapsed"
    >
      <template #icon>
        <n-icon :component="isCollapsed ? ExpandIcon : CompressIcon" />
      </template>
      <template v-if="showBtnText">
        {{
          isCollapsed ? expandText || $t('common.expand') : collapseText || $t('common.collapse')
        }}
      </template>
    </n-button>
  </div>
</template>

<style scoped>
.collapsed {
  position: relative;
}

.collapsed-shadow {
  display: none;
}

.collapsed > .collapsed-shadow {
  display: block;
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 10px;
  box-shadow: rgba(0, 0, 0, 0.175) 0px -40px 12px -40px inset;
  border-radius: var(--border-radius);
}
</style>
