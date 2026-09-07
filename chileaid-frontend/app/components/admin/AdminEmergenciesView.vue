<script setup lang="ts">
/**
 * VIEW — Gestión de emergencias del administrador. Puramente visual: recibe todo
 * por props y comunica intenciones por eventos. No importa la capa de datos; los
 * mapeos de label/color de `tipo`/`estado` viven inline (mismo patrón que
 * AdminCatalogView/AdminOrgsView).
 */
import BaseButton from '~/components/ui/BaseButton.vue'
import type { EmergencyDTO } from '~/services/adminEmergenciesService'

/** Valores del filtro por estado (mismos que acepta el ViewModel). */
type EstadoFiltro = 'todas' | 'activa' | 'cerrada'

defineProps<{
  emergencies: EmergencyDTO[]
  isLoading: boolean
  error: string | null
  closingId: string | null
  selectedEstado: string
  estadoCounts: Record<string, number>
}>()

const emit = defineEmits<{
  'open-create': []
  'close-emergency': [id: string]
  'set-estado': [estado: EstadoFiltro]
}>()

/** Etiqueta legible del tipo de emergencia (value del enum → texto). */
const TIPO_LABEL: Record<string, string> = {
  terremoto: 'Terremoto',
  incendio: 'Incendio',
  aluvion: 'Aluvión',
  otro: 'Otro'
}

/** Pills del filtro por estado. */
const FILTROS: { value: EstadoFiltro; label: string }[] = [
  { value: 'todas', label: 'Todas' },
  { value: 'activa', label: 'Activas' },
  { value: 'cerrada', label: 'Cerradas' }
]

/** Pide confirmación antes de emitir el cierre (patrón de la UI del proyecto). */
function onClose(em: EmergencyDTO): void {
  if (
    window.confirm(
      `¿Cerrar la emergencia "${em.nombre}"? Dejará de mostrarse a los donantes. ` +
        'No se puede reabrir.'
    )
  ) {
    emit('close-emergency', em.id)
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#f0f4ff] pb-24 pt-6 md:pb-6 md:pt-20">
    <div class="mx-auto max-w-5xl px-4 sm:px-6">
      <!-- Header -->
      <header class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 class="font-display text-3xl font-black uppercase tracking-wide text-navy-800">
            Emergencias
          </h1>
          <p class="mt-1 text-slate-500">
            {{ estadoCounts.activa ?? 0 }} activas · {{ estadoCounts.todas ?? 0 }} en total
          </p>
        </div>
        <BaseButton variant="navy" size="md" @click="emit('open-create')">
          + Nueva emergencia
        </BaseButton>
      </header>

      <!-- Filtro por estado -->
      <div class="mt-5 flex flex-wrap gap-2">
        <button
          v-for="f in FILTROS"
          :key="f.value"
          type="button"
          class="rounded-full px-3 py-1.5 text-xs font-bold uppercase tracking-widest
                 transition-colors"
          :class="selectedEstado === f.value
            ? 'bg-navy-800 text-white'
            : 'border border-navy-600/20 text-slate-500 hover:bg-navy-800/5'"
          @click="emit('set-estado', f.value)"
        >
          {{ f.label }} ({{ estadoCounts[f.value] ?? 0 }})
        </button>
      </div>

      <!-- Error -->
      <p
        v-if="error"
        role="alert"
        class="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-600"
      >
        {{ error }}
      </p>

      <!-- Loading -->
      <div v-if="isLoading" class="mt-6 flex flex-col gap-4">
        <div v-for="n in 3" :key="n" class="h-28 animate-pulse rounded-2xl bg-slate-200" />
      </div>

      <!-- Vacío -->
      <div
        v-else-if="emergencies.length === 0"
        class="glass-auth mt-6 rounded-2xl px-6 py-12 text-center"
      >
        <p class="text-sm text-slate-500">No hay emergencias para este filtro.</p>
      </div>

      <!-- Lista -->
      <ul v-else class="mt-6 flex flex-col gap-4">
        <li
          v-for="em in emergencies"
          :key="em.id"
          class="glass-auth rounded-2xl p-5 sm:p-6"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span
                  class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="em.estado === 'activa'
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-slate-200 text-slate-600'"
                >
                  {{ em.estado === 'activa' ? 'Activa' : 'Cerrada' }}
                </span>
                <span class="rounded-full bg-navy-800/8 px-2.5 py-0.5 text-xs font-semibold text-navy-800">
                  {{ TIPO_LABEL[em.tipo] ?? em.tipo }}
                </span>
              </div>
              <h2 class="mt-2 font-display text-lg font-bold text-navy-800">
                {{ em.nombre }}
              </h2>
              <p class="mt-0.5 text-sm text-slate-500">
                {{ em.zona }} · desde {{ em.fechaInicio }}
              </p>
            </div>

            <div class="text-right">
              <p class="font-display text-2xl font-black text-navy-800">
                {{ em.totalCentros }}
              </p>
              <p class="text-xs uppercase tracking-widest text-slate-400">
                {{ em.totalCentros === 1 ? 'centro' : 'centros' }}
              </p>
            </div>
          </div>

          <!-- Cobertura + acción -->
          <div class="mt-4 flex items-center justify-between gap-4">
            <div class="flex-1">
              <div class="flex items-center justify-between text-xs text-slate-500">
                <span>Cobertura</span>
                <span class="font-semibold text-navy-800">{{ em.cobertura }}%</span>
              </div>
              <div class="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-200">
                <div
                  class="h-full rounded-full bg-navy-600"
                  :style="{ width: `${em.cobertura}%` }"
                />
              </div>
            </div>
            <button
              v-if="em.estado === 'activa'"
              type="button"
              :disabled="closingId === em.id"
              class="shrink-0 rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold
                     text-slate-600 transition-colors hover:bg-slate-100 disabled:opacity-50"
              @click="onClose(em)"
            >
              {{ closingId === em.id ? 'Cerrando…' : 'Cerrar emergencia' }}
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
