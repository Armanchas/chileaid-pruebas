<script setup lang="ts">
/**
 * VIEW — Botón de cerrar sesión, compartido por las navbars (org/donor/admin).
 *
 * Cierra la sesión con `useAuth().logout()` (limpia token+rol en memoria y las
 * cookies `chileaid_token`/`chileaid_role`, y redirige a `/login`) sin
 * confirmación previa. Es la única excepción "de sesión" en una navbar autónoma:
 * no consume services ni DTOs, solo la infraestructura de auth.
 *
 * Dos presentaciones según `variant`:
 *  - `desktop`: pill horizontal (ícono + texto), a juego con los ítems del `<ul>`.
 *  - `mobile`: ítem de la bottom nav (`flex-1`, ícono + label corto), a juego con
 *    los `NuxtLink` hermanos.
 */
const props = withDefaults(
  defineProps<{ variant?: 'desktop' | 'mobile' }>(),
  { variant: 'desktop' }
)

const { logout } = useAuth()

async function onLogout(): Promise<void> {
  await logout()
}
</script>

<template>
  <!-- Desktop: pill con ícono + texto -->
  <button
    v-if="props.variant === 'desktop'"
    type="button"
    class="flex items-center gap-2 rounded-lg px-3 py-2 font-display text-sm font-bold
           uppercase tracking-widest text-slate-500 transition-colors duration-200
           hover:bg-alert/5 hover:text-alert"
    @click="onLogout"
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
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
    Cerrar sesión
  </button>

  <!-- Mobile: ítem de la bottom nav (ícono + label corto) -->
  <button
    v-else
    type="button"
    class="flex flex-1 flex-col items-center justify-center gap-1 text-slate-500
           transition-colors duration-200 hover:text-alert"
    aria-label="Cerrar sesión"
    @click="onLogout"
  >
    <span class="flex h-7 w-12 items-center justify-center rounded-full">
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
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
        <polyline points="16 17 21 12 16 7" />
        <line x1="21" y1="12" x2="9" y2="12" />
      </svg>
    </span>
    <span class="font-display text-[11px] font-bold uppercase tracking-wide">
      Salir
    </span>
  </button>
</template>
