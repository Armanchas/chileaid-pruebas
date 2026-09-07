<script setup lang="ts">
import { computed } from 'vue'
import { labelTipoCentro, colorTipoCentro, descripcionTipoCentro } from '~/utils/tipoCentro'
import type { CenterStatus, CenterType, EmergencyDTO } from '~/services/donorCentersService'

/**
 * VIEW — Encabezado del detalle de un centro. Puramente visual: recibe datos
 * por props y emite `go-back` (la página decide la navegación). El mapeo
 * color/etiqueta de tipo y estado es lógica de presentación.
 */
const props = defineProps<{
  nombre: string
  organizacion: string
  region: string
  direccion: string
  horario: string
  estado: CenterStatus
  tipoCentro: CenterType
  emergencia: EmergencyDTO | null
  cobertura: number
}>()

const emit = defineEmits<{
  'go-back': []
}>()

/** Etiqueta y color del badge de la emergencia asociada (nunca bg-alert). */
const tipoLabel: Record<EmergencyDTO['tipo'], string> = {
  terremoto: 'Terremoto',
  incendio: 'Incendio',
  aluvion: 'Aluvión',
  otro: 'Otro'
}
const tipoBadgeClass: Record<EmergencyDTO['tipo'], string> = {
  incendio: 'bg-orange-100 text-orange-800 border border-orange-200',
  terremoto: 'bg-red-100 text-red-800 border border-red-200',
  aluvion: 'bg-blue-100 text-blue-800 border border-blue-200',
  otro: 'bg-slate-100 text-slate-700 border border-slate-200'
}

/** Configuración visual del indicador de estado del centro. */
const statusConfig = computed(() => {
  switch (props.estado) {
    case 'critico':
      return { dot: 'bg-alert', pulse: true, label: 'Crítico', text: 'text-alert' }
    case 'cerrado':
      return { dot: 'bg-slate-400', pulse: false, label: 'Cerrado', text: 'text-slate-500' }
    default:
      return { dot: 'bg-green-500', pulse: false, label: 'En capacidad', text: 'text-green-700' }
  }
})

/** Color de la barra de cobertura según el porcentaje cubierto. */
const coberturaBarClass = computed(() => {
  if (props.cobertura >= 70) return 'bg-green-500'
  if (props.cobertura >= 30) return 'bg-amber-400'
  return 'bg-red-500'
})
const coberturaWidth = computed(
  () => `${Math.min(100, Math.max(0, props.cobertura))}%`
)
</script>

<template>
  <header>
    <!-- Breadcrumb -->
    <nav class="flex items-center gap-1 text-sm text-navy-600">
      <NuxtLink to="/donor/centers" class="hover:underline" @click="emit('go-back')">
        Centros
      </NuxtLink>
      <span class="text-slate-400">/</span>
      <span class="truncate text-slate-400">{{ nombre }}</span>
    </nav>

    <!-- Badge de emergencia + tipo de centro + estado -->
    <div class="mt-4 flex flex-wrap items-center gap-2">
      <span
        v-if="emergencia"
        class="rounded-full px-2.5 py-0.5 font-display text-xs font-bold uppercase tracking-widest"
        :class="tipoBadgeClass[emergencia.tipo]"
      >
        {{ tipoLabel[emergencia.tipo] }}
      </span>
      <span
        class="rounded-full px-3 py-1 text-sm font-bold"
        :class="colorTipoCentro(tipoCentro)"
      >
        {{ labelTipoCentro(tipoCentro) }}
      </span>
      <span class="text-sm text-slate-500">
        {{ descripcionTipoCentro(tipoCentro) }}
      </span>
      <span
        v-if="emergencia"
        class="font-display text-xs font-bold uppercase tracking-widest text-slate-400"
      >
        {{ emergencia.nombre }}
      </span>
    </div>

    <!-- Nombre del centro -->
    <div class="mt-2 flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0">
        <h1 class="font-display text-3xl font-black uppercase leading-tight text-navy-800 md:text-4xl">
          {{ nombre }}
        </h1>
        <p class="mt-1 text-slate-500">
          {{ organizacion }} · {{ region }}
        </p>
      </div>

      <!-- Badge de estado del centro -->
      <span class="flex shrink-0 items-center gap-1.5">
        <span
          class="h-2.5 w-2.5 rounded-full"
          :class="[statusConfig.dot, statusConfig.pulse ? 'alert-pulse' : '']"
        />
        <span
          class="font-display text-xs font-bold uppercase tracking-widest"
          :class="statusConfig.text"
        >
          {{ statusConfig.label }}
        </span>
      </span>
    </div>

    <!-- Horario + dirección -->
    <div class="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1.5 text-sm text-navy-600">
      <span class="flex items-center gap-1.5">
        <svg
          class="h-4 w-4 shrink-0 text-navy-600"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5l3 2" />
        </svg>
        {{ horario }}
      </span>
      <span class="flex items-center gap-1.5">
        <svg
          class="h-4 w-4 shrink-0 text-navy-600"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M12 21s-7-5.2-7-11a7 7 0 0 1 14 0c0 5.8-7 11-7 11z" />
          <circle cx="12" cy="10" r="2.5" />
        </svg>
        {{ direccion }}
      </span>
    </div>

    <!-- Barra de cobertura general del centro -->
    <div class="mt-5">
      <div class="h-2 w-full overflow-hidden rounded-full bg-navy-800/8">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="coberturaBarClass"
          :style="{ width: coberturaWidth }"
        />
      </div>
      <p class="mt-1.5 text-sm font-semibold text-navy-800">
        Cobertura general {{ cobertura }}%
      </p>
    </div>
  </header>
</template>
