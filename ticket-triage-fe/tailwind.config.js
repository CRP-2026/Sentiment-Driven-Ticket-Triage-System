/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        priority: {
          critical: "#EF4444",
          medium: "#F59E0B",
          low: "#10B981",
        },
      },
    },
  },
  plugins: [],
};
