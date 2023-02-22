import { type GlobalThemeOverrides, lightTheme } from 'naive-ui';
import _merge from 'lodash.merge';
import Color from 'color';

const commonOverrides: GlobalThemeOverrides = {
  common: {
    fontSize: '16px',
    fontSizeMini: '14px',
    fontSizeTiny: '14px',
    fontSizeSmall: '16px',
    fontSizeMedium: '16px',
    fontSizeLarge: '17px',
    fontSizeHuge: '18px',
    lineHeight: '1.8',
  },
  Form: {
    feedbackPadding: '4px 0 8px 2px',
    feedbackHeightSmall: '18px',
    feedbackHeightMedium: '18px',
    feedbackHeightLarge: '20px',
  },
};

const lightOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#ffffff',
  },
};

const darkOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#232323',
    primaryColor: Color(lightTheme.common.primaryColor).lighten(0.2).hex(),
    primaryColorHover: Color(lightTheme.common.primaryColorHover).lighten(0.2).saturate(0.5).hex(),
    primaryColorPressed: Color(lightTheme.common.primaryColorPressed).lighten(0.2).hex(),
    primaryColorSuppl: Color(lightTheme.common.primaryColorSuppl).lighten(0.2).hex(),
  },
  Card: {
    colorEmbedded: '#2a2a2a',
  },
};

_merge(lightOverrides, commonOverrides);
_merge(darkOverrides, commonOverrides);

export { lightOverrides, darkOverrides };
