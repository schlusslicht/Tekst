import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';
import { GET, type AnyResourceRead, type ResourceCoverage } from '@/api';
import { useAuthStore, useStateStore } from '@/stores';
import { hashCode } from '@/utils';

export const useResourcesStore = defineStore('resources', () => {
  const state = useStateStore();
  const auth = useAuthStore();

  const resourcesAll = ref<AnyResourceRead[]>([]);
  const resourcesOfText = computed(() =>
    resourcesAll.value.filter((r) => r.textId === state.text?.id)
  );
  const dataHash = computed(() => hashCode(resourcesAll.value));
  const error = ref(false);

  const loading = ref(false);

  function sortResources(res: AnyResourceRead[]) {
    return res.sort(
      (a, b) => (a.config?.common?.sortOrder ?? 0) - (b.config?.common?.sortOrder ?? 0)
    );
  }

  async function load() {
    if (loading.value) {
      return;
    }
    loading.value = true;
    error.value = false;

    const { data, error: err } = await GET('/resources'); // fetch ALL resources

    if (!err) {
      resourcesAll.value = sortResources(
        data.map((r) => {
          const existingResource = resourcesAll.value.find((re) => re.id === r.id);
          return {
            ...r,
            active: !!existingResource?.active || !!r.config?.common?.defaultActive,
            contents: existingResource?.contents ?? [],
          };
        })
      );
      error.value = false;
    } else {
      error.value = true;
    }
    loading.value = false;
  }

  function replace(resource: AnyResourceRead) {
    if (resourcesAll.value.find((re) => re.id === resource.id)) {
      resourcesAll.value = sortResources(
        resourcesAll.value.map((r) =>
          r.id === resource.id ? { ...resource, active: r.active, contents: r.contents } : r
        )
      );
    } else {
      add(resource);
    }
  }

  function add(resource: AnyResourceRead) {
    resource.active = resource.config?.common?.defaultActive;
    resourcesAll.value = sortResources(resourcesAll.value.concat([resource]));
  }

  function remove(resourceId: string) {
    resourcesAll.value = resourcesAll.value.filter((r) => r.id !== resourceId);
  }

  async function getCoverage(resourceId: string): Promise<ResourceCoverage | undefined> {
    const res = resourcesAll.value.find((r) => r.id === resourceId);
    if (!res) return;
    const cov = res?.coverage;
    if (cov) return cov;
    const { data } = await GET('/browse/resources/{id}/coverage', {
      params: { path: { id: resourceId } },
    });
    if (!data) return;
    res.coverage = data;
    return data;
  }

  function resetCoverage(resourceId?: string) {
    if (!resourceId) return;
    const res = resourcesAll.value.find((l) => l.id === resourceId);
    if (!res) return;
    res.coverage = undefined;
  }

  function setResourcesActiveState(resourceIds: string[], active: boolean) {
    resourcesAll.value = resourcesAll.value.map((r) => {
      if (resourceIds.includes(r.id)) {
        return {
          ...r,
          active,
        };
      }
      return r;
    });
  }

  // watch for events that trigger a reload of resources data
  watch(
    [() => auth.loggedIn, () => state.text],
    () => {
      load();
    },
    { immediate: true }
  );

  return {
    all: resourcesAll,
    ofText: resourcesOfText,
    dataHash,
    error,
    loading,
    load,
    replace,
    add,
    remove,
    getCoverage,
    resetCoverage,
    setResourcesActiveState,
  };
});
