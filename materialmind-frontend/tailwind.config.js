/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        blueprint: {
          950: '#0B1E2D',
          900: '#122A3D',
          800: '#1B3A52',
          700: '#274C68',
        },
        line: '#2A4A5F',
        paper: '#EDEFE9',
        steel: {
          400: '#7C93A3',
          300: '#9FB2BE',
        },
        brass: {
          500: '#C08552',
          400: '#D49A66',
        },
        copper: {
          400: '#E0A872',
        },
        alloy: {
          green: '#7FA88C',
        },
        rust: {
          500: '#B4552F',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      backgroundImage: {
        grid: 'linear-gradient(#2A4A5F 1px, transparent 1px), linear-gradient(90deg, #2A4A5F 1px, transparent 1px)',
      },
      backgroundSize: {
        grid: '32px 32px',
      },
    },
  },
  plugins: [],
}
