<script setup lang="ts">
/**
 * VIEW — Navbar reutilizable de la organización receptora. Autónoma: solo lee la
 * ruta actual con useRoute() para destacar el ítem activo y navega con NuxtLink.
 * No recibe props, no importa composables de datos ni contiene lógica de negocio.
 *
 * Responsive: barra horizontal fija arriba en desktop (md+); barra inferior fija
 * (bottom nav) en mobile. Ambas con estética .glass-light. Misma estructura que
 * DonorNavbar. Cierra sesión con el `LogoutButton` compartido.
 */
import LogoutButton from '~/components/shared/LogoutButton.vue'

const route = useRoute()

interface NavItem {
  to: string
  label: string
  icon: 'home' | 'list' | 'inbox' | 'truck' | 'person'
}

const items: NavItem[] = [
  { to: '/org', label: 'Inicio', icon: 'home' },
  { to: '/org/needs', label: 'Necesidades', icon: 'list' },
  { to: '/org/receptions', label: 'Recepciones', icon: 'inbox' },
  { to: '/org/distribution', label: 'Distribución', icon: 'truck' },
  { to: '/org/profile', label: 'Perfil', icon: 'person' }
]

/** Inicio (/org) activa solo en match exacto; el resto también en subrutas. */
function isActive(to: string): boolean {
  if (to === '/org') return route.path === '/org'
  return route.path === to || route.path.startsWith(`${to}/`)
}
</script>

<template>
  <!-- Desktop: barra superior fija horizontal -->
  <header class="glass-light fixed inset-x-0 top-0 z-40 hidden h-14 md:block">
    <nav class="mx-auto flex h-full max-w-5xl items-center justify-between px-6">
      <NuxtLink
        to="/org"
        class="font-display text-xl font-black uppercase tracking-tight text-navy-800"
      >
        Chile Aid
      </NuxtLink>

      <div class="flex items-center gap-2">
        <ul class="flex items-center gap-1">
          <li v-for="item in items" :key="item.to">
            <NuxtLink
              :to="item.to"
              class="flex items-center gap-2 rounded-lg px-3 py-2 font-display text-sm font-bold
                     uppercase tracking-widest transition-colors duration-200"
              :class="isActive(item.to)
                ? 'bg-navy-800/8 text-navy-800'
                : 'text-slate-500 hover:bg-navy-800/5 hover:text-navy-800'"
            >
              <svg
                class="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <template v-if="item.icon === 'home'">
                  <path d="M3 11.5 12 4l9 7.5" />
                  <path d="M5 10v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9" />
                </template>
                <template v-else-if="item.icon === 'list'">
                  <path d="M8 6h13" />
                  <path d="M8 12h13" />
                  <path d="M8 18h13" />
                  <path d="M3 6h.01" />
                  <path d="M3 12h.01" />
                  <path d="M3 18h.01" />
                </template>
                <template v-else-if="item.icon === 'inbox'">
                  <path d="M22 12h-6l-2 3h-4l-2-3H2" />
                  <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
                </template>
                <template v-else-if="item.icon === 'truck'">
                  <rect x="1" y="3" width="15" height="13" />
                  <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
                  <circle cx="5.5" cy="18.5" r="2.5" />
                  <circle cx="18.5" cy="18.5" r="2.5" />
                </template>
                <template v-else>
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1" />
                </template>
              </svg>
              {{ item.label }}
            </NuxtLink>
          </li>
        </ul>
        <LogoutButton variant="desktop" />
      </div>
    </nav>
  </header>

  <!-- Mobile: barra inferior fija (bottom nav) -->
  <nav class="glass-light fixed inset-x-0 bottom-0 z-40 flex h-[60px] items-stretch md:hidden">
    <NuxtLink
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="flex flex-1 flex-col items-center justify-center gap-1 transition-colors duration-200"
      :class="isActive(item.to) ? 'text-navy-800' : 'text-slate-500'"
    >
      <span
        class="flex h-7 w-12 items-center justify-center rounded-full transition-colors duration-200"
        :class="isActive(item.to) ? 'bg-navy-800/8' : ''"
      >
        <svg
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <template v-if="item.icon === 'home'">
            <path d="M3 11.5 12 4l9 7.5" />
            <path d="M5 10v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9" />
          </template>
          <template v-else-if="item.icon === 'list'">
            <path d="M8 6h13" />
            <path d="M8 12h13" />
            <path d="M8 18h13" />
            <path d="M3 6h.01" />
            <path d="M3 12h.01" />
            <path d="M3 18h.01" />
          </template>
          <template v-else-if="item.icon === 'inbox'">
            <path d="M22 12h-6l-2 3h-4l-2-3H2" />
            <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
          </template>
          <template v-else-if="item.icon === 'truck'">
            <rect x="1" y="3" width="15" height="13" />
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
            <circle cx="5.5" cy="18.5" r="2.5" />
            <circle cx="18.5" cy="18.5" r="2.5" />
          </template>
          <template v-else>
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1" />
          </template>
        </svg>
      </span>
      <span class="font-display text-[11px] font-bold uppercase tracking-wide">
        {{ item.label }}
      </span>
    </NuxtLink>
    <LogoutButton variant="mobile" />
  </nav>
</template>
