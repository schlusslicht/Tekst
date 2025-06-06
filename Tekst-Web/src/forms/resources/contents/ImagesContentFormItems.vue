<script setup lang="ts">
import type { ImagesContentCreate, ImagesResourceRead } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import OskInput from '@/components/OskInput.vue';
import { useMessages } from '@/composables/messages';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { checkUrl } from '@/utils';
import { cloneDeep } from 'lodash-es';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';
import { defaultContentModels } from './defaultContentModels';

defineProps<{
  resource: ImagesResourceRead;
}>();

const model = defineModel<ImagesContentCreate>({ required: true });
const { message } = useMessages();

async function checkUrlInput(input: HTMLInputElement) {
  const url = input.value;
  if (url && !(await checkUrl(url))) {
    message.warning($t('contents.warnUrlInvalid', { url }), undefined, 3);
    input.style.color = 'var(--error-color)';
  } else {
    input.style.color = 'var(--success-color)';
  }
}
</script>

<template>
  <!-- FILES -->
  <n-form-item :show-label="false" path="files">
    <n-dynamic-input
      v-model:value="model.files"
      :min="1"
      :max="100"
      :create-button-props="dynInputCreateBtnProps"
      item-class="divided"
      @create="() => cloneDeep(defaultContentModels.images.files[0])"
    >
      <template #default="{ index }">
        <n-flex align="stretch" style="flex: 2">
          <n-flex vertical style="flex: 2 240px">
            <!-- URL -->
            <n-form-item
              ignore-path-change
              :label="$t('resources.types.images.contentFields.imageUrl')"
              :path="`files[${index}].url`"
              :rule="contentFormRules.images.url"
            >
              <n-input
                v-model:value="model.files[index].url"
                :placeholder="$t('common.url')"
                @input-blur="checkUrlInput($event.target as HTMLInputElement)"
                @keydown.enter.prevent
              />
            </n-form-item>
            <!-- THUMBNAIL URL -->
            <n-form-item
              ignore-path-change
              :label="$t('resources.types.images.contentFields.thumbUrl')"
              :path="`files[${index}].thumbUrl`"
              :rule="contentFormRules.common.optionalUrl"
            >
              <n-input
                v-model:value="model.files[index].thumbUrl"
                :placeholder="$t('common.url')"
                @input-blur="checkUrlInput($event.target as HTMLInputElement)"
                @keydown.enter.prevent
              />
            </n-form-item>
            <!-- Source URL -->
            <n-form-item
              ignore-path-change
              :label="$t('resources.types.images.contentFields.sourceUrl')"
              :path="`files[${index}].sourceUrl`"
              :rule="contentFormRules.common.optionalUrl"
            >
              <n-input
                v-model:value="model.files[index].sourceUrl"
                :placeholder="$t('resources.types.images.contentFields.sourceUrl')"
                @keydown.enter.prevent
              />
            </n-form-item>
          </n-flex>
          <!-- CAPTION -->
          <n-form-item
            ignore-path-change
            :label="$t('common.caption')"
            :path="`files[${index}].caption`"
            :rule="contentFormRules.images.caption"
            style="flex: 2 240px"
          >
            <osk-input
              v-model="model.files[index].caption"
              type="textarea"
              class="caption-textarea"
              :font="resource.config.general.font || undefined"
              :osk-key="resource.config.general.osk || undefined"
              style="height: 100%"
              :max-length="512"
              :placeholder="$t('common.caption')"
              :dir="resource.config.general.rtl ? 'rtl' : undefined"
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          top-offset
          movable
          :insert-disabled="(model.files.length || 0) >= 100"
          :remove-disabled="model.files.length <= 1"
          :move-up-disabled="index === 0"
          :move-down-disabled="index === model.files.length - 1"
          @remove="() => remove(index)"
          @insert="() => create(index)"
          @move-up="move('up', index)"
          @move-down="move('down', index)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>

<style scoped>
:deep(.caption-textarea.n-input.n-input--textarea.n-input--resizable .n-input-wrapper) {
  resize: none;
}
</style>
