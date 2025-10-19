/**
 * REIMS Comprehensive Color System
 * 
 * A professional, vibrant color palette designed specifically for
 * real estate intelligence and data visualization
 */

export const reimsColors = {
  // ============================================================================
  // PRIMARY BRAND COLORS - Trust & Professionalism
  // ============================================================================
  // Psychology: Blue = Trust, Stability, Intelligence (essential for real estate)
  // Teal = Innovation, Balance, Modern (financial technology)
  
  brand: {
    // Main Brand Blue - Primary actions, headers, key UI elements
    blue: {
      50: '#EBF5FF',   // Lightest - backgrounds, hover states
      100: '#D6EBFF',  // Very light - subtle highlights
      200: '#AED7FF',  // Light - secondary backgrounds
      300: '#85C3FF',  // Medium light - borders, dividers
      400: '#5CAFFF',  // Medium - interactive elements
      500: '#2563EB',  // PRIMARY - main brand color
      600: '#1E50C7',  // Dark - hover states
      700: '#1740A3',  // Darker - active states
      800: '#10307F',  // Very dark - emphasis
      900: '#0A205B',  // Darkest - high contrast text
    },
    
    // Teal Accent - Modern, innovative touch
    teal: {
      50: '#E6FFFA',   // Lightest
      100: '#B2F5EA',  // Very light
      200: '#81E6D9',  // Light
      300: '#4FD1C5',  // Medium light
      400: '#38B2AC',  // Medium
      500: '#2C9A8B',  // PRIMARY teal
      600: '#257A6F',  // Dark
      700: '#1E5B53',  // Darker
      800: '#174537',  // Very dark
      900: '#10301B',  // Darkest
    },
  },

  // ============================================================================
  // ACCENT COLORS - Feature Highlighting
  // ============================================================================
  
  accent: {
    // Purple - AI/ML Features, Premium Features
    // Psychology: Purple = Innovation, Creativity, Intelligence, Premium
    purple: {
      50: '#FAF5FF',   // Lightest
      100: '#E9D8FD',  // Very light
      200: '#D6BCFA',  // Light
      300: '#B794F6',  // Medium light
      400: '#9F7AEA',  // Medium
      500: '#805AD5',  // PRIMARY purple - AI features
      600: '#6B46C1',  // Dark
      700: '#553C9A',  // Darker
      800: '#44337A',  // Very dark
      900: '#322659',  // Darkest
    },
    
    // Indigo - Analytics, Reports, Secondary Features
    // Psychology: Indigo = Depth, Wisdom, Insight (perfect for analytics)
    indigo: {
      50: '#EEF2FF',   // Lightest
      100: '#E0E7FF',  // Very light
      200: '#C7D2FE',  // Light
      300: '#A5B4FC',  // Medium light
      400: '#818CF8',  // Medium
      500: '#6366F1',  // PRIMARY indigo - analytics
      600: '#4F46E5',  // Dark
      700: '#4338CA',  // Darker
      800: '#3730A3',  // Very dark
      900: '#312E81',  // Darkest
    },
    
    // Cyan - Data Insights, Cool Features
    // Psychology: Cyan = Clarity, Focus, Communication
    cyan: {
      50: '#ECFEFF',   // Lightest
      100: '#CFFAFE',  // Very light
      200: '#A5F3FC',  // Light
      300: '#67E8F9',  // Medium light
      400: '#22D3EE',  // Medium
      500: '#06B6D4',  // PRIMARY cyan - insights
      600: '#0891B2',  // Dark
      700: '#0E7490',  // Darker
      800: '#155E75',  // Very dark
      900: '#164E63',  // Darkest
    },
  },

  // ============================================================================
  // POSITIVE METRICS - Success & Growth
  // ============================================================================
  // Psychology: Green = Growth, Success, Profit, Positive (universal positive)
  
  growth: {
    // Emerald Green - Main success color
    emerald: {
      50: '#ECFDF5',   // Lightest
      100: '#D1FAE5',  // Very light
      200: '#A7F3D0',  // Light
      300: '#6EE7B7',  // Medium light
      400: '#34D399',  // Medium
      500: '#10B981',  // PRIMARY success green
      600: '#059669',  // Dark
      700: '#047857',  // Darker
      800: '#065F46',  // Very dark
      900: '#064E3B',  // Darkest
    },
    
    // Lime - High growth, exceptional performance
    lime: {
      50: '#F7FEE7',   // Lightest
      100: '#ECFCCB',  // Very light
      200: '#D9F99D',  // Light
      300: '#BEF264',  // Medium light
      400: '#A3E635',  // Medium
      500: '#84CC16',  // PRIMARY lime - exceptional
      600: '#65A30D',  // Dark
      700: '#4D7C0F',  // Darker
      800: '#3F6212',  // Very dark
      900: '#365314',  // Darkest
    },
  },

  // ============================================================================
  // STATUS & ALERT COLORS - System States
  // ============================================================================
  
  status: {
    // Success - Completed, Approved, Healthy
    success: {
      50: '#ECFDF5',
      100: '#D1FAE5',
      200: '#A7F3D0',
      300: '#6EE7B7',
      400: '#34D399',
      500: '#10B981',  // PRIMARY success
      600: '#059669',
      700: '#047857',
      800: '#065F46',
      900: '#064E3B',
    },
    
    // Warning - Attention needed, Review required
    // Psychology: Yellow = Caution, Attention (universal warning)
    warning: {
      50: '#FFFBEB',
      100: '#FEF3C7',
      200: '#FDE68A',
      300: '#FCD34D',
      400: '#FBBF24',
      500: '#F59E0B',  // PRIMARY warning
      600: '#D97706',
      700: '#B45309',
      800: '#92400E',
      900: '#78350F',
    },
    
    // Error/Critical - Failed, Rejected, Critical issues
    // Psychology: Red = Danger, Stop, Critical (universal danger)
    error: {
      50: '#FEF2F2',
      100: '#FEE2E2',
      200: '#FECACA',
      300: '#FCA5A5',
      400: '#F87171',
      500: '#EF4444',  // PRIMARY error
      600: '#DC2626',
      700: '#B91C1C',
      800: '#991B1B',
      900: '#7F1D1D',
    },
    
    // Info - Informational, Updates, Notifications
    // Psychology: Blue = Information, Communication
    info: {
      50: '#EFF6FF',
      100: '#DBEAFE',
      200: '#BFDBFE',
      300: '#93C5FD',
      400: '#60A5FA',
      500: '#3B82F6',  // PRIMARY info
      600: '#2563EB',
      700: '#1D4ED8',
      800: '#1E40AF',
      900: '#1E3A8A',
    },
  },

  // ============================================================================
  // DATA VISUALIZATION - Chart Colors
  // ============================================================================
  // Carefully selected for clarity, distinction, and accessibility
  
  chart: {
    // Primary chart colors (high contrast, colorblind-friendly)
    primary: '#2563EB',    // Blue
    secondary: '#10B981',  // Green
    tertiary: '#F59E0B',   // Amber
    quaternary: '#8B5CF6', // Purple
    
    // Extended palette for complex charts
    palette: [
      '#2563EB', // Blue - primary data
      '#10B981', // Green - positive/growth
      '#F59E0B', // Amber - neutral/warning
      '#EF4444', // Red - negative/critical
      '#8B5CF6', // Purple - special/AI
      '#06B6D4', // Cyan - insights
      '#EC4899', // Pink - highlights
      '#F97316', // Orange - important
      '#6366F1', // Indigo - analytics
      '#14B8A6', // Teal - balance
    ],
    
    // Gradient pairs for area charts
    gradients: {
      blue: ['#2563EB', '#93C5FD'],
      green: ['#10B981', '#6EE7B7'],
      purple: ['#8B5CF6', '#C4B5FD'],
      teal: ['#14B8A6', '#5EEAD4'],
    },
    
    // Heatmap colors (cool to warm)
    heatmap: [
      '#1E3A8A', // Cool dark
      '#2563EB', // Cool
      '#60A5FA', // Cool light
      '#F3F4F6', // Neutral
      '#FCD34D', // Warm light
      '#F59E0B', // Warm
      '#DC2626', // Hot
    ],
  },

  // ============================================================================
  // NEUTRAL COLORS - Backgrounds, Text, Borders
  // ============================================================================
  // Psychology: Neutrals provide balance, readability, sophistication
  
  neutral: {
    // Cool gray - Modern, clean, professional
    slate: {
      50: '#F8FAFC',   // Lightest - main background
      100: '#F1F5F9',  // Very light - card backgrounds
      200: '#E2E8F0',  // Light - borders, dividers
      300: '#CBD5E1',  // Medium light - disabled states
      400: '#94A3B8',  // Medium - placeholders
      500: '#64748B',  // Base - secondary text
      600: '#475569',  // Dark - body text
      700: '#334155',  // Darker - headings
      800: '#1E293B',  // Very dark - emphasis
      900: '#0F172A',  // Darkest - high contrast
    },
    
    // True gray - Balanced, versatile
    gray: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
    },
  },

  // ============================================================================
  // DARK MODE VARIANTS - Night Theme
  // ============================================================================
  // Optimized for reduced eye strain and OLED displays
  
  dark: {
    // Background layers
    bg: {
      primary: '#0F172A',    // Main background
      secondary: '#1E293B',  // Card background
      tertiary: '#334155',   // Elevated elements
      overlay: '#475569',    // Overlays, modals
    },
    
    // Text colors
    text: {
      primary: '#F8FAFC',    // Main text
      secondary: '#CBD5E1',  // Secondary text
      tertiary: '#94A3B8',   // Muted text
      disabled: '#64748B',   // Disabled text
    },
    
    // Border colors
    border: {
      primary: '#334155',    // Main borders
      secondary: '#475569',  // Emphasized borders
      subtle: '#1E293B',     // Subtle dividers
    },
  },

  // ============================================================================
  // FUNCTIONAL COLORS - Specific UI Elements
  // ============================================================================
  
  functional: {
    // Interactive elements
    interactive: {
      hover: 'rgba(37, 99, 235, 0.1)',    // Subtle hover
      active: 'rgba(37, 99, 235, 0.2)',   // Active state
      focus: 'rgba(37, 99, 235, 0.3)',    // Focus ring
    },
    
    // Overlays and shadows
    overlay: {
      light: 'rgba(0, 0, 0, 0.05)',
      medium: 'rgba(0, 0, 0, 0.1)',
      dark: 'rgba(0, 0, 0, 0.2)',
      darker: 'rgba(0, 0, 0, 0.4)',
    },
    
    // Gradients for premium features
    gradients: {
      brand: 'linear-gradient(135deg, #2563EB 0%, #14B8A6 100%)',
      ai: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
      success: 'linear-gradient(135deg, #10B981 0%, #84CC16 100%)',
      premium: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
    },
  },
}

export default reimsColors

















