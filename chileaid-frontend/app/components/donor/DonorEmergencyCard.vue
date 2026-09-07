<script setup lang="ts">
import { computed } from 'vue'
import type { EmergencyDTO } from '~/services/donorCentersService'

/**
 * VIEW — Tarjeta de una emergencia activa. Puramente visual: recibe el DTO por
 * prop y emite `select` con el id. No conoce servicios ni composables; el
 * mapeo de color/etiqueta es lógica de presentación, no de negocio.
 */
const props = defineProps<{
  emergency: EmergencyDTO
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

/** Etiqueta legible del tipo de emergencia. */
const tipoLabel: Record<EmergencyDTO['tipo'], string> = {
  terremoto: 'Terremoto',
  incendio: 'Incendio',
  aluvion: 'Aluvión',
  otro: 'Otro'
}

/** Color semántico propio del badge de tipo (nunca bg-alert). */
const tipoBadgeClass: Record<EmergencyDTO['tipo'], string> = {
  incendio: 'bg-orange-100 text-orange-800 border border-orange-200',
  terremoto: 'bg-red-100 text-red-800 border border-red-200',
  aluvion: 'bg-blue-100 text-blue-800 border border-blue-200',
  otro: 'bg-slate-100 text-slate-700 border border-slate-200'
}

/** Color de la barra de cobertura según el porcentaje cubierto. */
const coberturaBarClass = computed(() => {
  const c = props.emergency.cobertura
  if (c >= 70) return 'bg-green-500'
  if (c >= 30) return 'bg-amber-400'
  return 'bg-red-500'
})

const coberturaWidth = computed(
  () => `${Math.min(100, Math.max(0, props.emergency.cobertura))}%`
)

/** Fecha de inicio en formato legible (es-CL), determinista para SSR. */
const MESES = [
  'ene', 'feb', 'mar', 'abr', 'may', 'jun',
  'jul', 'ago', 'sep', 'oct', 'nov', 'dic'
]
const fechaLegible = computed(() => {
  const [year, month, day] = props.emergency.fechaInicio.split('-')
  const mes = MESES[Number(month) - 1] ?? ''
  return `${Number(day)} ${mes} ${year}`
})
</script>

<template>
  <article
    class="glass-auth flex flex-col rounded-2xl p-5 transition-all duration-200
           hover:-translate-y-0.5 hover:shadow-lg hover:shadow-navy-800/10"
  >
    <div class="flex items-start justify-between gap-3">
      <span
        class="rounded-full px-2.5 py-0.5 font-display text-xs font-bold uppercase tracking-widest"
        :class="tipoBadgeClass[emergency.tipo]"
      >
        {{ tipoLabel[emergency.tipo] }}
      </span>
      <span class="font-display text-xs font-bold uppercase tracking-widest text-slate-400">
        {{ emergency.totalCentros }} {{ emergency.totalCentros === 1 ? 'centro' : 'centros' }} activos
      </span>
    </div>

    <h3 class="mt-3 font-display text-2xl font-black uppercase leading-tight text-navy-800">
      {{ emergency.nombre }}
    </h3>
    <p class="mt-1 text-sm text-slate-500">
      {{ emergency.zona }} · Desde el {{ fechaLegible }}
    </p>

    <!-- Barra de cobertura agregada -->
    <div class="mt-4">
      <div class="h-2 w-full overflow-hidden rounded-full bg-navy-800/8">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="coberturaBarClass"
          :style="{ width: coberturaWidth }"
        />
      </div>
      <p class="mt-1.5 text-sm font-semibold text-navy-800">
        Cobertura {{ emergency.cobertura }}%
      </p>
    </div>

    <button
      type="button"
      class="mt-4 inline-flex items-center justify-center gap-2 rounded-lg border border-navy-600/25
             px-4 py-2.5 font-display text-sm font-bold uppercase tracking-wide text-navy-600
             transition-colors duration-200 hover:bg-navy-800/5
             focus:outline-none focus-visible:ring-4 focus-visible:ring-navy-600/20"
      @click="emit('select', emergency.id)"
    >
      Ver centros
    </button>
  </article>
</template>
