// https://nuxt.com/docs/api/configuration/nuxt-config

// URL base de la API (FastAPI). `apiBase` la usa el NAVEGADOR (y SSR en local);
// `apiBaseServer` la usa el SSR cuando corre en un entorno donde el backend no
// está en "localhost" (p. ej. Docker Compose, donde se llega por el nombre de
// servicio `backend`). Si NUXT_API_BASE_SERVER no está definida, cae a `apiBase`,
// así el desarrollo local (npm run dev) se comporta exactamente igual que antes.
const apiBase = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
const apiBaseServer = process.env.NUXT_API_BASE_SERVER || apiBase

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  runtimeConfig: {
    // Privado: solo disponible en el servidor (SSR). Override: NUXT_API_BASE_SERVER.
    apiBaseServer,
    public: {
      // Público: expuesto al navegador. Override: NUXT_PUBLIC_API_BASE.
      apiBase
    }
  },

  modules: [
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/image',
    '@nuxtjs/tailwindcss'
  ],

  css: ['~/assets/css/main.css'],

  // @nuxt/fonts descarga y autohospeda las familias declaradas en CSS.
  // Títulos: Barlow Condensed / Oswald en pesos 800-900 (NO Inter ni Space Grotesk).
  fonts: {
    families: [
      { name: 'Barlow Condensed', provider: 'google', weights: [400, 600, 700, 800, 900] },
      { name: 'Oswald', provider: 'google', weights: [500, 700, 800] }
    ]
  },

  app: {
    head: {
      title: 'Chile Aid — Coordinando la ayuda donde más se necesita',
      htmlAttrs: { lang: 'es' },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Plataforma de gestión de donaciones humanitarias en Chile. Conectamos donantes con organizaciones receptoras verificadas mostrando necesidades en tiempo real.'
        },
        { name: 'theme-color', content: '#002675' }
      ]
    }
  }
})
