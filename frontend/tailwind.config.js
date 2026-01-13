export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        quantum: {
          50: '#f0f4ff',
          100: '#e6edff',
          500: '#6366f1',
          600: '#4f46e5',
          900: '#1e1b4b',
        }
      }
    },
  },
  plugins: [],
}
