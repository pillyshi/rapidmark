import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// Material Design 3 theme configuration
const lightTheme = {
  dark: false,
  colors: {
    primary: '#1976d2',
    'primary-darken-1': '#1565c0',
    secondary: '#03dac6',
    'secondary-darken-1': '#018786',
    accent: '#82b1ff',
    error: '#ba1a1a',
    info: '#2196f3',
    success: '#146c2e',
    warning: '#7d5260',
    
    // Material Design 3 surface colors
    background: '#fafafa',
    surface: '#ffffff',
    'surface-variant': '#f5f5f5',
    'on-surface': '#1c1b1f',
    'on-surface-variant': '#49454f',
    outline: '#79747e',
    'outline-variant': '#cac4d0',
  }
}

const darkTheme = {
  dark: true,
  colors: {
    primary: '#90caf9',
    'primary-darken-1': '#64b5f6',
    secondary: '#4dd0e1',
    'secondary-darken-1': '#26c6da',
    accent: '#ff4081',
    error: '#ffb4ab',
    info: '#81c784',
    success: '#a5d6a7',
    warning: '#ffcc02',
    
    // Material Design 3 dark surface colors
    background: '#121212',
    surface: '#121212',
    'surface-variant': '#1e1e1e',
    'on-surface': '#e6e1e5',
    'on-surface-variant': '#cac4d0',
    outline: '#938f96',
    'outline-variant': '#49454f',
  }
}

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: lightTheme,
      dark: darkTheme,
    },
    variations: {
      colors: ['primary', 'secondary'],
      lighten: 4,
      darken: 4,
    },
  },
  defaults: {
    VBtn: {
      style: 'text-transform: none;', // Disable uppercase transformation
      rounded: 'lg',
    },
    VCard: {
      rounded: 'lg',
      elevation: 2,
    },
    VDialog: {
      rounded: 'xl',
    },
    VOverlay: {
      rounded: 'lg',
    },
    VTabs: {
      density: 'compact',
    },
    VChip: {
      rounded: 'lg',
    },
  },
})