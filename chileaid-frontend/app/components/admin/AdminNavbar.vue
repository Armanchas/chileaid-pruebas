<script setup lang="ts">
/**
 * VIEW — Navbar reutilizable del panel de administración. Autónoma: solo lee la
 * ruta actual con useRoute() para destacar el ítem activo y navega con NuxtLink.
 * No recibe props, no importa composables de datos ni contiene lógica de negocio.
 *
 * Responsive: barra horizontal fija arriba en desktop (md+); barra inferior fija
 * (bottom nav) en mobile. Ambas con estética .glass-light. Misma estructura que
 * OrgNavbar. Cierra sesión con el `LogoutButton` compartido.
 */
import LogoutButton from '~/components/shared/LogoutButton.vue'

const route = useRoute()

interface NavItem {
  to: string
  label: string
  icon: 'chart' | 'building' | 'list' | 'alert'
}

const items: NavItem[] = [
  { to: '/admin', label: 'Dashboard', icon: 'chart' },
  { to: '/admin/orgs', label: 'Organizaciones', icon: 'building' },
  { to: '/admin/emergencies', label: 'Emergencias', icon: 'alert' },
  { to: '/admin/catalog', label: 'Catálogo', icon: 'list' }
]

/** Dashboard (/admin) activa solo en match exacto; el resto también en subrutas. */
function isActive(to: string): boolean {
  if (to === '/admin') return route.path === '/admin'
  return route.path === to || route.path.startsWith(`${to}/`)
}
</script>

<template>
  <!-- Desktop: barra superior fija horizontal -->
  <header class="glass-light fixed inset-x-0 top-0 z-40 hidden h-14 md:block">
    <nav
      aria-label="Navegación principal de administración"
      class="mx-auto flex h-full max-w-5xl items-center justify-between px-6"
    >
      <NuxtLink
        to="/admin"
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
                <template v-if="item.icon === 'chart'">
                  <path d="M3 3v18h18" />
                  <path d="M7 15l3-4 3 3 4-6" />
                </template>
                <template v-else-if="item.icon === 'building'">
                  <rect x="4" y="3" width="16" height="18" rx="1" />
                  <path d="M9 7h.01" />
                  <path d="M15 7h.01" />
                  <path d="M9 11h.01" />
                  <path d="M15 11h.01" />
                  <path d="M10 21v-4h4v4" />
                </template>
                <template v-else-if="item.icon === 'alert'">
                  <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <path d="M12 9v4" />
                  <path d="M12 17h.01" />
                </template>
                <template v-else>
                  <path d="M8 6h13" />
                  <path d="M8 12h13" />
                  <path d="M8 18h13" />
                  <path d="M3 6h.01" />
                  <path d="M3 12h.01" />
                  <path d="M3 18h.01" />
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
    aria-label="Navegación móvil de administración"
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
          <template v-if="item.icon === 'chart'">
            <path d="M3 3v18h18" />
            <path d="M7 15l3-4 3 3 4-6" />
          </template>
          <template v-else-if="item.icon === 'building'">
            <rect x="4" y="3" width="16" height="18" rx="1" />
            <path d="M9 7h.01" />
            <path d="M15 7h.01" />
            <path d="M9 11h.01" />
            <path d="M15 11h.01" />
            <path d="M10 21v-4h4v4" />
          </template>
          <template v-else-if="item.icon === 'alert'">
            <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <path d="M12 9v4" />
            <path d="M12 17h.01" />
          </template>
          <template v-else>
            <path d="M8 6h13" />
            <path d="M8 12h13" />
            <path d="M8 18h13" />
            <path d="M3 6h.01" />
            <path d="M3 12h.01" />
            <path d="M3 18h.01" />
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
