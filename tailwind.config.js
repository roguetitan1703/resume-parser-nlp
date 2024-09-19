// tailwind.config.js
module.exports = {
  content: [
    "./app/templates/**/*.html", // Point to your HTML templates
  ],
  theme: {
    extend: {
      zIndex: {
        9999: "9999",
      },
      scale: {
        101: "1.01",
      },
      // Add custom utilities
      maskImage: {
        "gradient-bottom": "linear-gradient(to bottom, transparent, black)",
      },
      webkitMaskImage: {
        "gradient-bottom":
          "-webkit-linear-gradient(to bottom, transparent, black)",
      },
    },
  },
  plugins: [
    function ({ addUtilities }) {
      const newUtilities = {
        ".mask-gradient-bottom": {
          maskImage: "linear-gradient(to bottom, transparent, black)",
        },
        ".webkit-mask-gradient-bottom": {
          WebkitMaskImage:
            "-webkit-linear-gradient(to bottom, transparent, black)",
        },
      };
      addUtilities(newUtilities);
    },
  ],
};
