<script setup lang="ts">
import type {
  AnnotationAggregation,
  TextAnnotationResourceRead,
  TextAnnotationSearchQuery,
} from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { NSelect, NFormItem, NDynamicInput } from 'naive-ui';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { searchFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { computed, onMounted, ref } from 'vue';
import { useResourcesStore } from '@/stores';

const props = defineProps<{
  resource: TextAnnotationResourceRead;
  queryIndex: number;
}>();
const model = defineModel<TextAnnotationSearchQuery>({ required: true });

const resources = useResourcesStore();

const annoValueStyle = {
  fontFamily: props.resource.config?.general?.font || 'Tekst Content Font',
};

const aggregations = ref<AnnotationAggregation[]>([]);
const annoOptions = computed(() => {
  const keysOptions = aggregations.value.map((agg) => ({ label: agg.key, value: agg.key }));
  const anyValueOption = {
    label: () => $t('resources.types.textAnnotation.searchFields.any'),
    value: '',
  };
  return (
    model.value.anno?.map((a) => ({
      keysOptions,
      valuesOptions: [
        anyValueOption,
        ...(aggregations.value
          .find((agg) => agg.key === a.k)
          ?.values?.map((v) => ({ label: v, value: v, style: annoValueStyle })) || []),
      ],
    })) || []
  );
});

function getAnnoValueSelectStyle(value?: string) {
  return value ? annoValueStyle : undefined;
}

function handleUpdate(field: string, value: any) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}

onMounted(async () => {
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <!-- TOKEN -->
  <n-form-item
    :label="$t('resources.types.textAnnotation.contentFields.token')"
    ignore-path-change
    :path="`queries[${queryIndex}].rts.token`"
    :rule="searchFormRules.textAnnotation.token"
    style="flex-grow: 1; flex-basis: 200px"
  >
    <n-input-osk
      :model-value="model.token"
      :font="resource.config?.general?.font || undefined"
      :placeholder="$t('resources.types.textAnnotation.contentFields.token')"
      @update:model-value="(v) => handleUpdate('token', v)"
    />
  </n-form-item>

  <!-- ANNOTATIONS -->
  <n-form-item
    :label="$t('resources.types.textAnnotation.contentFields.annotations')"
    :show-feedback="!model.anno?.length"
    style="flex-grow: 2; flex-basis: 400px"
  >
    <n-dynamic-input
      :value="model.anno"
      @update-value="(v) => handleUpdate('anno', v)"
      @create="() => ({ k: undefined, v: undefined })"
    >
      <template #default="{ value: annotationItem, index: annotationItemIndex }">
        <div
          style="
            display: flex;
            flex-wrap: wrap;
            flex-grow: 2;
            gap: var(--gap-md);
            align-items: flex-start;
          "
        >
          <n-form-item
            style="flex-grow: 2; flex-basis: 200px"
            :show-label="false"
            ignore-path-change
            :path="`queries[${queryIndex}].rts.anno[${annotationItemIndex}].k`"
            :rule="searchFormRules.textAnnotation.annotationKey"
          >
            <n-select
              v-model:value="annotationItem.k"
              filterable
              clearable
              :options="annoOptions[annotationItemIndex].keysOptions"
              :placeholder="$t('resources.types.textAnnotation.contentFields.annotationKey')"
              @update:value="() => (annotationItem.v = '')"
            />
          </n-form-item>
          <n-form-item
            style="flex-grow: 2; flex-basis: 200px"
            :show-label="false"
            ignore-path-change
            :path="`queries[${queryIndex}].rts.anno[${annotationItemIndex}].v`"
            :rule="searchFormRules.textAnnotation.annotationValue"
          >
            <n-select
              v-model:value="annotationItem.v"
              tag
              filterable
              clearable
              :disabled="!annotationItem.k"
              :style="getAnnoValueSelectStyle(annotationItem.v)"
              :options="annoOptions[annotationItemIndex].valuesOptions"
              :placeholder="$t('resources.types.textAnnotation.contentFields.annotationValue')"
            />
          </n-form-item>
        </div>
      </template>
      <template
        #action="{
          index: annotationActionIndex,
          create: createAnnotation,
          remove: removeAnnotation,
        }"
      >
        <dynamic-input-controls
          :movable="false"
          :insert-disabled="annotationActionIndex >= 63"
          @remove="() => removeAnnotation(annotationActionIndex)"
          @insert="() => createAnnotation(annotationActionIndex)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
