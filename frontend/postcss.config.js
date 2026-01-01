// PostCSS configuration for Tailwind CSS v4
// PostCSS processes CSS files and applies Tailwind transformations
// Tailwind CSS v4 requires @tailwindcss/postcss instead of tailwindcss directly
export default {
  plugins: {
    '@tailwindcss/postcss': {},  // Tailwind CSS v4 PostCSS plugin
    autoprefixer: {},  // Adds vendor prefixes for better browser compatibility
  },
}

