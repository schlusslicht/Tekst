import { type MenuOption } from 'naive-ui';
import { h, computed } from 'vue';
import { RouterLink, type RouteLocationRaw } from 'vue-router';
import { $t } from '@/i18n';
import { useBrowseStore, useStateStore } from '@/stores';
import { usePlatformData } from '@/composables/platformData';
import type { ClientSegmentHead } from '@/api';
import { pickTranslation, renderIcon } from '@/utils';

import {
  EyeIcon,
  ManageAccountIcon,
  TextsIcon,
  BarChartIcon,
  AddCircleIcon,
  SettingsIcon,
  InfoIcon,
  BookIcon,
  SearchIcon,
  MaintenanceIcon,
  SystemIcon,
  SegmentsIcon,
  UsersIcon,
  LevelsIcon,
  TreeIcon,
} from '@/icons';

function renderLink(
  label: string | (() => string),
  to: RouteLocationRaw,
  props?: Record<string, unknown>
) {
  return () =>
    h(
      RouterLink,
      {
        ...props,
        to,
        style: {
          fontSize: 'var(--font-size)',
        },
      },
      { default: label }
    );
}

export function useMainMenuOptions(showIcons: boolean = true) {
  const { pfData } = usePlatformData();
  const state = useStateStore();
  const browse = useBrowseStore();

  const infoPagesOptions = computed(() => {
    const pages: ClientSegmentHead[] = [];
    // add pages with current locale
    pages.push(...(pfData.value?.infoSegments.filter((p) => p.locale === state.locale) || []));
    // add pages without locale
    pages.push(
      ...(pfData.value?.infoSegments.filter(
        (p) => p.locale === '*' && !pages.find((i) => i.key === p.key)
      ) || [])
    );
    // add pages with enUS locale (fallback)
    pages.push(
      ...(pfData.value?.infoSegments.filter(
        (p) => p.locale === 'enUS' && !pages.find((i) => i.key === p.key)
      ) || [])
    );
    return pages.map((p) => ({
      label: renderLink(() => p.title || p.key, { name: 'info', params: { p: p.key } }),
      key: `page_${p.key}`,
      icon: (showIcons && renderIcon(InfoIcon)) || undefined,
    }));
  });

  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(() => $t('nav.browse'), {
        name: 'browse',
        params: { text: state.text?.slug },
        query: { lvl: browse.level, pos: browse.position },
      }),
      key: 'browse',
      icon: (showIcons && renderIcon(BookIcon)) || undefined,
    },
    {
      label: renderLink(() => $t('nav.search'), {
        name: 'search',
        params: { text: state.text?.slug },
      }),
      key: 'search',
      icon: (showIcons && renderIcon(SearchIcon)) || undefined,
    },
    ...(infoPagesOptions.value.length
      ? [
          {
            label: () =>
              pickTranslation(pfData.value?.settings.navInfoEntry, state.locale) || $t('nav.info'),
            key: 'info',
            children: infoPagesOptions.value,
          },
        ]
      : []),
  ]);

  return {
    menuOptions,
  };
}

export function useAccountMenuOptions(showIcons: boolean = true) {
  const menuOptions: MenuOption[] = [
    {
      label: renderLink(() => $t('account.profile'), { name: 'accountProfile' }),
      key: 'accountProfile',
      icon: (showIcons && renderIcon(EyeIcon)) || undefined,
    },
    {
      label: renderLink(() => $t('account.account'), { name: 'accountSettings' }),
      key: 'accountSettings',
      icon: (showIcons && renderIcon(ManageAccountIcon)) || undefined,
    },
  ];

  return {
    menuOptions,
  };
}

export function useAdminMenuOptions(showIcons: boolean = true) {
  const state = useStateStore();

  const menuOptions = computed<MenuOption[]>(() => [
    {
      label: renderLink(() => $t('admin.statistics.heading'), { name: 'adminStatistics' }),
      key: 'adminStatistics',
      icon: (showIcons && renderIcon(BarChartIcon)) || undefined,
    },
    {
      label: $t('admin.text.heading'),
      key: 'adminText',
      icon: (showIcons && renderIcon(TextsIcon)) || undefined,
      children: [
        {
          label: renderLink(() => $t('admin.text.settings.heading'), {
            name: 'adminTextsSettings',
            params: { text: state.text?.slug },
          }),
          key: 'adminTextsSettings',
          icon: (showIcons && renderIcon(SettingsIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.text.levels.heading'), {
            name: 'adminTextsLevels',
            params: { text: state.text?.slug },
          }),
          key: 'adminTextsLevels',
          icon: (showIcons && renderIcon(LevelsIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.text.locations.heading'), {
            name: 'adminTextsLocations',
            params: { text: state.text?.slug },
          }),
          key: 'adminTextsLocations',
          icon: (showIcons && renderIcon(TreeIcon)) || undefined,
        },
      ],
    },
    {
      label: renderLink(() => $t('admin.newText.heading'), { name: 'adminNewText' }),
      key: 'adminNewText',
      icon: (showIcons && renderIcon(AddCircleIcon)) || undefined,
    },
    {
      label: $t('admin.system.heading'),
      key: 'adminSystem',
      icon: (showIcons && renderIcon(SystemIcon)) || undefined,
      children: [
        {
          label: renderLink(() => $t('admin.system.platformSettings.heading'), {
            name: 'adminSystemSettings',
          }),
          key: 'adminSystemSettings',
          icon: (showIcons && renderIcon(SettingsIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.system.infoPages.heading'), {
            name: 'adminSystemInfoPages',
          }),
          key: 'adminSystemInfoPages',
          icon: (showIcons && renderIcon(InfoIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.system.segments.heading'), {
            name: 'adminSystemSegments',
          }),
          key: 'adminSystemSegments',
          icon: (showIcons && renderIcon(SegmentsIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.users.heading'), { name: 'adminSystemUsers' }),
          key: 'adminSystemUsers',
          icon: (showIcons && renderIcon(UsersIcon)) || undefined,
        },
        {
          label: renderLink(() => $t('admin.system.maintenance.heading'), {
            name: 'adminSystemMaintenance',
          }),
          key: 'adminSystemMaintenance',
          icon: (showIcons && renderIcon(MaintenanceIcon)) || undefined,
        },
      ],
    },
  ]);

  return {
    menuOptions,
  };
}
