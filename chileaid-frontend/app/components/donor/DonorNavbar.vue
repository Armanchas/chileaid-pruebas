<script setup lang="ts">
/**
 * VIEW — Navbar reutilizable del donante. Autónoma: solo lee la ruta actual
 * con useRoute() para destacar el ítem activo y navega con NuxtLink. No recibe
 * props, no importa composables de datos ni contiene lógica de negocio.
 *
 * Responsive: barra horizontal fija arriba en desktop (md+); barra inferior
 * fija (bottom nav) en mobile. Ambas con estética .glass-light. Cierra sesión
 * con el `LogoutButton` compartido.
 */
import LogoutButton from '~/components/shared/LogoutButton.vue'

const route = useRoute()

interface NavItem {
  to: string
  label: string
}

const items: NavItem[] = [
  { to: '/donor', label: 'Inicio' },
  { to: '/donor/centers', label: 'Centros' },
  { to: '/donor/map', label: 'Mapa' },
  { to: '/donor/profile', label: 'Perfil' }
]

/** Inicio (/donor) activa solo en match exacto; el resto también en subrutas. */
function isActive(to: string): boolean {
  if (to === '/donor') return route.path === '/donor'
  return route.path === to || route.path.startsWith(`${to}/`)
}
</script>

<template>
  <!-- Desktop: barra superior fija horizontal -->
  <header
    class="glass-light fixed inset-x-0 top-0 z-40 hidden h-14 md:block"
  >
    <nav class="mx-auto flex h-full max-w-5xl items-center justify-between px-6">
      <NuxtLink
        to="/donor"
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
                <template v-if="item.to === '/donor'">
                  <path d="M3 11.5 12 4l9 7.5" />
                  <path d="M5 10v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9" />
                </template>
                <template v-else-if="item.to === '/donor/centers'">
                  <path d="M3 21V8l9-5 9 5v13" />
                  <path d="M9 21v-6h6v6" />
                </template>
                <template v-else-if="item.to === '/donor/map'">
                  <path d="M12 21s-6-5.686-6-10a6 6 0 0 1 12 0c0 4.314-6 10-6 10z" />
                  <circle cx="12" cy="11" r="2.5" />
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
  <nav
    class="glass-light fixed inset-x-0 bottom-0 z-40 flex h-[60px] items-stretch md:hidden"
  >
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
          <template v-if="item.to === '/donor'">
            <path d="M3 11.5 12 4l9 7.5" />
            <path d="M5 10v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9" />
          </template>
          <template v-else-if="item.to === '/donor/centers'">
            <path d="M3 21V8l9-5 9 5v13" />
            <path d="M9 21v-6h6v6" />
          </template>
          <template v-else-if="item.to === '/donor/map'">
            <path d="M12 21s-6-5.686-6-10a6 6 0 0 1 12 0c0 4.314-6 10-6 10z" />
            <circle cx="12" cy="11" r="2.5" />
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
