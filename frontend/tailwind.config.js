/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        quantum: {
          green: "#7BAF29",
          yellow: "#F9B000"
        }
      },
      fontFamily: {
        sans: ['"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif']
      },
      boxShadow: {
        quantum: '0 4px 6px rgba(123, 175, 41, 0.3)'
      }
    }
  },
  plugins: []
}
