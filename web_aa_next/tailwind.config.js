/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'aa-red': {
          DEFAULT: '#E30613',
          dark: '#C00510',
          light: '#FF0F1F',
        },
        'aa-blue': {
          DEFAULT: '#005799',
          dark: '#004175',
          light: '#0070BD',
        },
      },
    },
  },
  plugins: [],
}