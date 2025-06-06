<script setup lang="ts">
import type { LocationRead, TextRead } from '@/api';
import { GET } from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { NDivider, NForm, NFormItem, NSelect } from 'naive-ui';
import { computed, onMounted, ref, watch } from 'vue';

const props = withDefaults(
  defineProps<{
    allowLevelChange?: boolean;
  }>(),
  {
    allowLevelChange: true,
  }
);

const model = defineModel<LocationRead[]>({ required: true });

const state = useStateStore();
const { message } = useMessages();

const lvl = ref(Math.max(0, model.value.length - 1));
const lvlOptions = computed(() =>
  state.textLevelLabels.map((l, i) => ({
    value: i,
    label: l + (state.text?.defaultLevel === i ? ` (${$t('common.default')})` : ''),
  }))
);
// react to level selection changes
watch(lvl, (after, before) => {
  if (after > before) {
    updateSelectModels(before);
  }
  applyBrowseLevel();
});

// interface for location select options (internal component state)
interface LocationSelectModel {
  loading: boolean;
  selected: string | null;
  disabled: boolean;
  locations: LocationRead[];
}
const locationSelectModels = ref<LocationSelectModel[]>(getEmptyModels());
const loading = computed(() => locationSelectModels.value.some((lsm) => lsm.loading));

// generate location select options from select model locations
const locationSelectOptions = computed(() =>
  locationSelectModels.value.map((lsm) =>
    lsm.locations.map((n) => ({
      label: n.label,
      value: n.id,
    }))
  )
);

function getEmptyModels(text: TextRead | undefined = state.text): LocationSelectModel[] {
  if (!text) return [];
  return (
    text.levels.map((_, i) => ({
      loading: false,
      selected: null,
      locations: [],
      options: [],
      disabled: props.allowLevelChange && i > lvl.value,
    })) || []
  );
}

async function updateSelectModels(fromLvl: number = 0) {
  // abort if the highest enabled level was changed (nothing to do)
  if (fromLvl >= locationSelectModels.value.length - 1) {
    updateModel();
    return;
  }
  // set loading state
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > fromLvl) {
      lsm.loading = true;
    }
  });
  // cancel if requested level has no selected location
  if (!locationSelectModels.value[fromLvl].selected) {
    return;
  }
  // load location path options from location selected at lvl as root
  const { data: locations, error } = await GET('/locations/{id}/path-options/{by}', {
    params: { path: { id: locationSelectModels.value[fromLvl].selected || '', by: 'root' } },
  });
  if (error) {
    updateModel();
    return;
  }
  // set locations for all following levels
  locationSelectModels.value.forEach((lsm, i) => {
    // only apply to higher levels
    if (i > fromLvl) {
      // only do this if we're <= current browse level
      if (i <= lvl.value) {
        // set locations
        lsm.locations = locations.shift() || [];
        // set selection
        lsm.selected = lsm.locations[0]?.id || null;
      }
      // set to no loading
      lsm.loading = false;
    }
  });
  updateModel();
}

function applyBrowseLevel() {
  locationSelectModels.value.forEach((lsm, i) => {
    lsm.disabled = props.allowLevelChange && i > lvl.value;
    lsm.locations = lsm.disabled ? [] : lsm.locations;
    lsm.selected = lsm.disabled ? null : lsm.selected;
  });
}

async function initSelectModels() {
  // set all live models to loading
  locationSelectModels.value.forEach((lsm) => {
    lsm.loading = true;
  });

  // fetch locations from head to root
  const reqLocId = model.value[lvl.value]?.id;
  if (!reqLocId) {
    return;
  }
  const { data: locationsOptions, error } = await GET('/locations/{id}/path-options/{by}', {
    params: { path: { id: reqLocId, by: 'head' } },
  });

  if (error) {
    message.error($t('errors.unexpected'), error);
    return;
  }
  // apply browse level
  applyBrowseLevel();

  // manipulate each location select model
  let index = 0;
  for (const lsm of locationSelectModels.value) {
    // set options and selection
    if (index <= lvl.value) {
      // remember locations for these options
      lsm.locations = locationsOptions[index];
      // set selection
      lsm.selected = model.value[index]?.id || null;
    }
    index++;
    lsm.loading = false;
  }
}

function updateModel() {
  model.value = locationSelectModels.value
    .filter((_, i) => i <= lvl.value)
    .map((lsm) => lsm.locations.find((n) => n.id === lsm.selected) || lsm.locations[0]);
}

onMounted(() => {
  initSelectModels();
});
</script>

<template>
  <n-form
    label-placement="left"
    label-width="auto"
    :show-feedback="false"
    :show-require-mark="false"
  >
    <template v-if="props.allowLevelChange">
      <n-form-item :label="$t('common.level')">
        <n-select
          v-model:value="lvl"
          :options="lvlOptions"
          :disabled="loading"
          :loading="loading"
          @update:value="updateSelectModels"
        />
      </n-form-item>

      <n-divider />
    </template>

    <template v-for="(levelLoc, index) in locationSelectModels" :key="`${index}_loc_select`">
      <n-form-item
        v-if="allowLevelChange || index <= lvl"
        :label="state.textLevelLabels[index]"
        class="location-select-item mb-sm"
        :class="{ disabled: levelLoc.disabled }"
      >
        <n-select
          v-model:value="levelLoc.selected"
          :options="locationSelectOptions[index]"
          filterable
          placeholder="–"
          :loading="loading"
          :disabled="loading || levelLoc.disabled || locationSelectOptions[index].length === 0"
          @update:value="() => updateSelectModels(index)"
        />
      </n-form-item>
    </template>
  </n-form>
</template>

<style scoped>
.text-location {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.location-select-item.disabled {
  opacity: 0.5;
}
</style>
