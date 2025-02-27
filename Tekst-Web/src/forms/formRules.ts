import type { FormItemRule } from 'naive-ui';
import { $t, localeProfiles } from '@/i18n';
import { resourceTypes } from '@/api';

function requiredStringRule(
  inputLabel: () => string,
  trigger?: FormItemRule['trigger']
): FormItemRule {
  return {
    required: true,
    message: () =>
      $t('forms.rulesFeedback.isRequired', {
        x: inputLabel(),
      }),
    trigger,
  };
}

function minMaxCharsRule(
  min: number,
  max: number,
  trigger?: FormItemRule['trigger']
): FormItemRule {
  return {
    validator: (rule: FormItemRule, value: string) =>
      (min <= 0 && !value) || (!!value && value.length >= min && value.length <= max),
    message: () => $t('forms.rulesFeedback.minMaxChars', { min, max }),
    trigger,
  };
}

export const translationFormRules: Record<string, FormItemRule[]> = {
  locale: [requiredStringRule(() => $t('models.locale.modelLabel'), 'blur')],
};

export const accountFormRules: Record<string, FormItemRule[]> = {
  email: [
    requiredStringRule(() => $t('models.user.email'), 'input'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^.+@.+\.\w+$/.test(value),
      message: () => $t('models.user.formRulesFeedback.emailInvalid'),
      trigger: 'input',
    },
  ],
  username: [
    requiredStringRule(() => $t('models.user.username'), 'blur'),
    minMaxCharsRule(4, 16, 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]*$/.test(value),
      message: () => $t('models.user.formRulesFeedback.usernameChars'),
      trigger: 'blur',
    },
  ],
  password: [
    requiredStringRule(() => $t('models.user.password'), 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && value.length >= 8,
      message: () => $t('forms.rulesFeedback.minChars', { min: 8 }),
      trigger: ['input', 'blur'],
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && /[a-z]/.test(value) && /[a-z]/.test(value) && /\d/.test(value),
      message: () => $t('models.user.formRulesFeedback.passwordChars'),
      trigger: ['input', 'blur'],
    },
  ],
  passwordRepeat: [
    {
      required: true,
      message: () => $t('models.user.formRulesFeedback.passwordRepReq'),
      trigger: 'blur',
    },
  ],
  name: [requiredStringRule(() => $t('models.user.name'), 'blur'), minMaxCharsRule(1, 64, 'blur')],
  affiliation: [
    requiredStringRule(() => $t('models.user.affiliation'), 'blur'),
    minMaxCharsRule(1, 180, 'blur'),
  ],
  avatarUrl: [minMaxCharsRule(0, 1024, 'blur')],
  bio: [minMaxCharsRule(0, 2000, 'blur')],
  loginEmail: [requiredStringRule(() => $t('models.user.email'), 'input')],
  loginPassword: [requiredStringRule(() => $t('models.user.password'), 'input')],
};

export const textFormRules: Record<string, FormItemRule[]> = {
  title: [
    requiredStringRule(() => $t('models.text.title'), 'blur'),
    minMaxCharsRule(1, 64, 'blur'),
  ],
  subtitleTranslation: [
    requiredStringRule(() => $t('models.text.subtitle'), 'blur'),
    minMaxCharsRule(1, 128, 'blur'),
  ],
  subtitleLocale: [requiredStringRule(() => $t('general.language'), 'blur')],
  slug: [
    requiredStringRule(() => $t('models.text.slug'), 'blur'),
    minMaxCharsRule(1, 16, 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-z0-9]+$/.test(value),
      message: () => $t('models.text.formRulesFeedback.slugChars'),
      trigger: ['input', 'blur'],
    },
  ],
  levels: [
    {
      validator: (rule: FormItemRule, value: any[]) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  levelTranslation: [
    requiredStringRule(() => $t('models.text.level'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  defaultLevel: [
    {
      validator: (rule: FormItemRule, value: number) => value != null && value >= 0,
      message: () => $t('models.text.formRulesFeedback.defaultLevelRange'),
      trigger: 'blur',
    },
  ],
  locDelim: [
    requiredStringRule(() => $t('models.text.locDelim'), 'blur'),
    minMaxCharsRule(1, 3, 'blur'),
  ],
  resourceCategoryKey: [
    requiredStringRule(() => $t('models.text.resourceCategoryKey'), 'blur'),
    minMaxCharsRule(1, 16, 'blur'),
  ],
  resourceCategoryTranslation: [
    requiredStringRule(() => $t('models.text.resourceCategoryTranslation'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
};

export const locationFormRules: Record<string, FormItemRule[]> = {
  label: [
    requiredStringRule(() => $t('models.location.label'), 'blur'),
    minMaxCharsRule(1, 256, 'blur'),
  ],
  aliases: [
    {
      validator: (rule: FormItemRule, value: any) =>
        value == null || (Array.isArray(value) && value.length <= 16),
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 0, max: 16 }),
      trigger: 'blur',
    },
  ],
};

export const correctionFormRules: Record<string, FormItemRule[]> = {
  note: [
    requiredStringRule(() => $t('browse.contents.widgets.correctionNote.lblNote'), 'blur'),
    minMaxCharsRule(1, 256, 'blur'),
  ],
};

export const systemSegmentFormRules: Record<string, FormItemRule[]> = {
  title: [minMaxCharsRule(0, 32, 'blur')],
  key: [requiredStringRule(() => $t('models.segment.key'), 'blur')],
  locale: [requiredStringRule(() => $t('models.segment.locale'), 'blur')],
  html: [
    requiredStringRule(() => $t('models.segment.html'), 'blur'),
    minMaxCharsRule(1, 1048576, 'blur'),
  ],
};

export const infoSegmentFormRules: Record<string, FormItemRule[]> = {
  title: [minMaxCharsRule(0, 32, 'blur')],
  key: [
    requiredStringRule(() => $t('models.segment.key'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]+$/.test(value),
      message: () => $t('models.segment.formRulesFeedback.keyChars'),
      trigger: ['input', 'blur'],
    },
    {
      validator: (rule: FormItemRule, value: string) => !!value && !value.startsWith('system'),
      message: () => $t('models.segment.formRulesFeedback.systemPrefixReserved'),
      trigger: 'blur',
    },
  ],
  locale: [requiredStringRule(() => $t('models.segment.locale'), 'blur')],
  html: [
    requiredStringRule(() => $t('models.segment.html'), 'blur'),
    minMaxCharsRule(1, 1048576, 'blur'),
  ],
};

export const platformSettingsFormRules: Record<string, FormItemRule[]> = {
  platformName: [
    requiredStringRule(() => $t('models.platformSettings.platformName'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  platformSubtitleTranslation: [minMaxCharsRule(1, 128, 'blur')],
  availableLocales: [
    {
      validator: (rule: FormItemRule, value: string[]) =>
        !!value &&
        value.length >= 1 &&
        value.length <= localeProfiles.length &&
        !value.find((v) => !localeProfiles.filter((lp) => lp.key === v).length),
      message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: localeProfiles.length }),
      trigger: 'blur',
    },
  ],
  navEntryTranslation: [minMaxCharsRule(1, 42, 'blur')],
  registerIntroTextTranslation: [minMaxCharsRule(1, 500, 'blur')],
  oskModeKey: [
    requiredStringRule(() => $t('models.platformSettings.oskModeKey'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  oskModeName: [
    requiredStringRule(() => $t('models.platformSettings.oskModeName'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
  resourceFontName: [
    requiredStringRule(() => $t('models.platformSettings.resourceFontName'), 'blur'),
    minMaxCharsRule(1, 32, 'blur'),
  ],
};

export const resourceSettingsFormRules: Record<string, FormItemRule[]> = {
  titleTranslation: [
    requiredStringRule(() => $t('models.resource.title'), 'blur'),
    minMaxCharsRule(1, 64, 'blur'),
  ],
  descriptionTranslation: [
    requiredStringRule(() => $t('models.resource.description'), 'blur'),
    minMaxCharsRule(1, 512, 'blur'),
  ],
  citation: [minMaxCharsRule(0, 1000, 'blur')],
  commentTranslation: [
    requiredStringRule(() => $t('general.comment'), 'blur'),
    minMaxCharsRule(1, 2000, 'blur'),
  ],
  metaKey: [
    requiredStringRule(() => $t('models.meta.key'), 'blur'),
    minMaxCharsRule(1, 16, 'blur'),
  ],
  metaValue: [
    requiredStringRule(() => $t('models.meta.value'), 'blur'),
    minMaxCharsRule(1, 128, 'blur'),
  ],
  resourceType: [
    requiredStringRule(() => $t('models.resource.resourceType'), 'blur'),
    {
      validator: (rule: FormItemRule, value: string) => !!value && resourceTypes.includes(value),
      message: () =>
        $t('forms.rulesFeedback.mustBeOneOf', {
          x: $t('models.resource.resourceType'),
          values: resourceTypes.join(', '),
        }),
      trigger: 'blur',
    },
  ],
  level: [
    {
      required: true,
      type: 'number',
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.resource.level'),
        }),
      trigger: 'blur',
    },
  ],
};

export const commonResourceConfigFormRules: Record<string, FormItemRule[]> = {
  sortOrder: [
    {
      required: true,
      type: 'number',
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('resources.settings.config.common.sortOrder'),
        }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: number) =>
        Number.isInteger(value) && value >= 0 && value <= 1000,
      message: '0-1000',
      trigger: 'blur',
    },
  ],
};

export const reducedViewConfigFormRules: Record<string, FormItemRule[]> = {
  singleLineDelimiter: [
    requiredStringRule(
      () => $t('resources.settings.config.reducedView.singleLineDelimiter'),
      'blur'
    ),
    minMaxCharsRule(1, 3, 'blur'),
  ],
};

export const typeSpecificResourceConfigFormRules: Record<string, Record<string, FormItemRule[]>> = {
  textAnnotation: {
    displayTemplate: [minMaxCharsRule(0, 2048, 'blur')],
    multiValueDelimiter: [
      requiredStringRule(() => $t('resources.settings.config.multiValueDelimiter'), 'blur'),
      minMaxCharsRule(1, 3, 'blur'),
    ],
  },
};

export const contentFormRules: Record<string, Record<string, FormItemRule[]>> = {
  common: {
    comment: [minMaxCharsRule(0, 50000, 'blur')],
    notes: [minMaxCharsRule(0, 1000, 'blur')],
    optionalUrl: [minMaxCharsRule(0, 2083, 'blur')],
    caption: [minMaxCharsRule(0, 8192, 'blur')],
  },
  plainText: {
    text: [
      requiredStringRule(() => $t('resources.types.plainText.contentFields.text'), 'blur'),
      minMaxCharsRule(1, 102400, 'blur'),
    ],
  },
  richText: {
    html: [
      requiredStringRule(() => $t('resources.types.richText.contentFields.html'), 'blur'),
      minMaxCharsRule(1, 102400, 'blur'),
    ],
  },
  textAnnotation: {
    token: [
      requiredStringRule(() => $t('resources.types.textAnnotation.contentFields.token'), 'blur'),
      minMaxCharsRule(1, 4096, 'blur'),
    ],
    annotationKey: [
      requiredStringRule(
        () => $t('resources.types.textAnnotation.contentFields.annotationKey'),
        'blur'
      ),
      minMaxCharsRule(1, 32, 'blur'),
    ],
    annotationValue: [
      {
        validator: (rule: FormItemRule, value: any) => !!value && Array.isArray(value),
        message: () =>
          $t('forms.rulesFeedback.isRequired', {
            x: $t('resources.types.textAnnotation.contentFields.annotationValue'),
          }),
        trigger: 'change',
      },
      {
        validator: (rule: FormItemRule, value: any[]) =>
          !!value && value.length >= 1 && value.length <= 64,
        message: () => $t('forms.rulesFeedback.minMaxItems', { min: 1, max: 64 }),
        trigger: 'change',
      },
      {
        validator: (rule: FormItemRule, value: any[]) =>
          !!value && value.every((item) => item.length >= 1 && item.length <= 256),
        message: () => $t('forms.rulesFeedback.minMaxChars', { min: 1, max: 256 }),
        trigger: 'change',
      },
    ],
  },
  audio: {
    url: [
      requiredStringRule(() => $t('resources.types.audio.contentFields.url'), 'blur'),
      minMaxCharsRule(1, 2083, 'blur'),
    ],
  },
  images: {
    url: [
      requiredStringRule(() => $t('resources.types.images.contentFields.url'), 'blur'),
      minMaxCharsRule(1, 2083, 'blur'),
    ],
  },
  externalReferences: {
    url: [
      requiredStringRule(() => $t('resources.types.externalReferences.contentFields.url'), 'blur'),
      minMaxCharsRule(1, 2083, 'blur'),
    ],
    title: [
      requiredStringRule(
        () => $t('resources.types.externalReferences.contentFields.title'),
        'blur'
      ),
      minMaxCharsRule(1, 128, 'blur'),
    ],
    description: [minMaxCharsRule(0, 4096, 'blur')],
  },
};

export const searchFormRules: Record<string, Record<string, FormItemRule[]>> = {
  common: {
    comment: [minMaxCharsRule(0, 512, 'blur')],
  },
  plainText: {
    text: [minMaxCharsRule(0, 512, 'blur')],
  },
  richText: {
    html: [minMaxCharsRule(0, 512, 'blur')],
  },
  textAnnotation: {
    token: [minMaxCharsRule(0, 512, 'blur')],
    annotationKey: [
      requiredStringRule(
        () => $t('resources.types.textAnnotation.contentFields.annotationKey'),
        'blur'
      ),
      minMaxCharsRule(1, 32, 'blur'),
    ],
    annotationValue: [minMaxCharsRule(0, 64, 'blur')],
  },
  audio: {
    caption: [minMaxCharsRule(0, 512, 'blur')],
  },
  images: {
    caption: [minMaxCharsRule(0, 512, 'blur')],
  },
  externalReferences: {
    caption: [minMaxCharsRule(0, 512, 'blur')],
  },
};

export const bookmarkFormRules: Record<string, FormItemRule[]> = {
  comment: [minMaxCharsRule(0, 1000, 'blur')],
};

export const wysiwygEditorFormRules: Record<string, FormItemRule[]> = {
  imageUrl: [minMaxCharsRule(0, 5000, undefined)],
  linkUrl: [minMaxCharsRule(0, 5000, undefined)],
};
