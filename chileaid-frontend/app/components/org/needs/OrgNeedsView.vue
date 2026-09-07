<script setup lang="ts">
/**
 * VIEW — Listado de necesidades publicadas por la organización. Puramente visual:
 * recibe todo por props y comunica intenciones por eventos. No conoce servicios
 * ni composables.
 *
 * Cada necesidad referencia un insumo del catálogo y muestra su cantidad
 * requerida; las urgentes se marcan con el indicador `alert` (mismo criterio que
 * el panel). Sin barras de cobertura: esta pantalla gestiona el catálogo de
 * necesidades (alta/edición/cierre), no su nivel de cumplimiento.
 */
import BaseButton from '~/components/ui/BaseButton.vue'
import type { NeedDTO, Urgencia } from '~/services/orgDashboardService'

defineProps<{
  needs: NeedDTO[]
  isLoading: boolean
  closingId: string | null
}>()

const emit = defineEmits<{
  'open-create': []
  'edit-need': [need: NeedDTO]
  'close-need': [id: string]
}>()

/** Clases del badge según el nivel de urgencia. */
const URGENCIA_BADGE: Record<Urgencia, string> = {
  alta: 'bg-alert text-white',
  media: 'bg-amber-100 text-amber-700',
  baja: 'bg-slate-100 text-slate-500'
}
/** Etiqueta legible del nivel de urgencia. */
const URGENCIA_LABEL: Record<Urgencia, string> = {
  alta: 'Urgente',
  media: 'Media',
  baja: 'Baja'
}
/** Etiqueta del estado para necesidades que ya no admiten acciones. */
const ESTADO_LABEL: Record<string, string> = {
  completada: 'Completada',
  cerrada: 'Cerrada'
}

/**
 * Pide confirmación antes de cerrar manualmente la necesidad (CU-03). El cierre
 * detiene nuevos aportes pero conserva los compromisos existentes.
 */
function confirmClose(need: NeedDTO): void {
  const ok = window.confirm(
    '¿Cerrar esta necesidad? Ya no podrá recibir nuevos aportes, pero los compromisos existentes se mantienen.'
  )
  if (ok) emit('close-need', need.id)
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
    <!-- ===== HEADER ===== -->
    <header class="flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0">
        <h1 class="font-display text-2xl font-black uppercase text-navy-800">
          Gestionar necesidades
        </h1>
        <p class="mt-1 text-slate-500">
          Publica y mantén al día lo que tu organización necesita recibir
        </p>
      </div>
      <BaseButton variant="navy" size="md" @click="emit('open-create')">
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
          <path d="M12 5v14" />
          <path d="M5 12h14" />
        </svg>
        Agregar nueva necesidad
      </BaseButton>
    </header>

    <!-- ===== LOADING (skeleton) ===== -->
    <div
      v-if="isLoading && needs.length === 0"
      class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <div
        v-for="n in 3"
        :key="n"
        class="h-40 animate-pulse rounded-2xl bg-slate-200"
      />
    </div>

    <!-- ===== VACÍO ===== -->
    <div
      v-else-if="needs.length === 0"
      class="glass-auth mt-6 rounded-2xl px-4 py-12 text-center"
    >
      <p class="text-sm text-slate-500">
        Aún no has publicado necesidades.
      </p>
      <p class="mt-1 text-sm text-slate-400">
        Usa “Agregar nueva necesidad” para que los donantes sepan qué requieres.
      </p>
    </div>

    <!-- ===== GRID DE NECESIDADES ===== -->
    <ul
      v-else
      class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <li
        v-for="need in needs"
        :key="need.id"
        class="glass-auth flex flex-col gap-3 rounded-2xl p-5"
        :class="closingId === need.id ? 'pointer-events-none opacity-50' : ''"
      >
        <!-- Encabezado: insumo + badge de urgencia -->
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <h2 class="font-display text-lg font-black uppercase leading-tight text-navy-800">
              {{ need.insumo.nombre }}
            </h2>
            <p class="mt-0.5 text-xs text-slate-400">
              {{ need.insumo.categoria }}
            </p>
          </div>
          <span
            class="inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-0.5
                   text-xs font-bold uppercase tracking-wide"
            :class="URGENCIA_BADGE[need.urgencia]"
          >
            <span
              v-if="need.urgencia === 'alta'"
              class="alert-pulse h-1.5 w-1.5 rounded-full bg-white"
              aria-hidden="true"
            />
            {{ URGENCIA_LABEL[need.urgencia] }}
          </span>
        </div>

        <!-- Cantidad requerida -->
        <p class="flex-1 text-sm text-slate-600">
          Requerido:
          <span class="font-semibold text-navy-800">
            {{ need.cantidadRequerida }} {{ need.insumo.unidad }}
          </span>
        </p>

        <!-- Acciones de la tarjeta: solo para necesidades ACTIVAS -->
        <div class="flex items-center gap-2 border-t border-slate-200/70 pt-3">
          <template v-if="need.estado === 'activa'">
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-display text-xs
                     font-bold uppercase tracking-widest text-navy-600 transition-colors
                     hover:bg-navy-800/8 hover:text-navy-800"
              @click="emit('edit-need', need)"
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
                <path d="M12 20h9" />
                <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
              </svg>
              Editar
            </button>
            <button
              type="button"
              :disabled="closingId === need.id"
              class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-display text-xs
                     font-bold uppercase tracking-widest text-slate-500 transition-colors
                     hover:bg-slate-100 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
              @click="confirmClose(need)"
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
                <circle cx="12" cy="12" r="10" />
                <path d="m15 9-6 6" />
                <path d="m9 9 6 6" />
              </svg>
              {{ closingId === need.id ? 'Cerrando…' : 'Cerrar' }}
            </button>
          </template>

          <!-- Necesidad ya cerrada/completada: sin acciones, solo el estado -->
          <span
            v-else
            class="font-display text-xs font-bold uppercase tracking-widest text-slate-400"
          >
            {{ ESTADO_LABEL[need.estado] ?? need.estado }}
          </span>
        </div>
      </li>
    </ul>
  </div>
</template>
