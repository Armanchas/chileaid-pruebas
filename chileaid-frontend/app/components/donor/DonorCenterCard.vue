<script setup lang="ts">
import { computed } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import { labelTipoCentro, colorTipoCentro } from '~/utils/tipoCentro'
import type { CenterDTO } from '~/services/donorCentersService'

/**
 * VIEW — Tarjeta de un centro de acopio. Puramente visual: recibe el DTO por
 * prop y emite `select` con el id. No conoce servicios ni composables; el
 * mapeo de estado/color es lógica de presentación.
 */
const props = defineProps<{
  center: CenterDTO
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

/** Máximo de chips de necesidades visibles antes de resumir el resto. */
const MAX_NEEDS = 3
const visibleNeeds = computed(() => props.center.necesidadesUrgentes.slice(0, MAX_NEEDS))
const extraNeeds = computed(() => Math.max(0, props.center.necesidadesUrgentes.length - MAX_NEEDS))

/** Configuración visual del indicador de estado del centro. */
const statusConfig = computed(() => {
  switch (props.center.estado) {
    case 'critico':
      return { dot: 'bg-alert', pulse: true, label: 'Crítico', text: 'text-alert' }
    case 'cerrado':
      return { dot: 'bg-slate-400', pulse: false, label: 'Cerrado', text: 'text-slate-500' }
    default:
      return { dot: 'bg-green-500', pulse: false, label: 'En capacidad', text: 'text-green-700' }
  }
})

const isCerrado = computed(() => props.center.estado === 'cerrado')

/** Color de la barra de cobertura según el porcentaje cubierto. */
const coberturaBarClass = computed(() => {
  const c = props.center.cobertura
  if (c >= 70) return 'bg-green-500'
  if (c >= 30) return 'bg-amber-400'
  return 'bg-red-500'
})

const coberturaWidth = computed(
  () => `${Math.min(100, Math.max(0, props.center.cobertura))}%`
)
</script>

<template>
  <article
    class="glass-auth flex w-full flex-col rounded-2xl p-5 transition-all duration-200
           hover:-translate-y-0.5 hover:shadow-lg hover:shadow-navy-800/10"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <h3 class="font-display text-xl font-black uppercase leading-tight text-navy-800">
          {{ center.nombre }}
        </h3>
        <p class="mt-0.5 text-sm text-slate-500">
          {{ center.organizacion }} · {{ center.zona }}
        </p>
        <span
          class="mt-1.5 inline-block rounded-full px-2 py-0.5 text-xs font-semibold"
          :class="colorTipoCentro(center.tipoCentro)"
        >
          {{ labelTipoCentro(center.tipoCentro) }}
        </span>
        <!-- Emergencia específica a la que responde el centro (nombre, no solo tipo) -->
        <span
          v-if="center.emergenciaNombre"
          class="mt-1.5 flex items-center gap-1 text-xs font-semibold text-navy-600"
        >
          <svg
            class="h-3.5 w-3.5 shrink-0"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <path d="M12 9v4" />
            <path d="M12 17h.01" />
          </svg>
          {{ center.emergenciaNombre }}
        </span>
      </div>

      <!-- Indicador de estado -->
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

    <!-- Chips de necesidades urgentes -->
    <div v-if="center.necesidadesUrgentes.length" class="mt-3 flex flex-wrap gap-1.5">
      <span
        v-for="need in visibleNeeds"
        :key="need"
        class="rounded-full bg-navy-800/8 px-2 py-0.5 text-xs text-navy-800"
      >
        {{ need }}
      </span>
      <span
        v-if="extraNeeds > 0"
        class="rounded-full bg-navy-800/8 px-2 py-0.5 text-xs text-navy-800"
      >
        +{{ extraNeeds }} más
      </span>
    </div>

    <!-- Barra de cobertura -->
    <div class="mt-4">
      <div class="h-2 w-full overflow-hidden rounded-full bg-navy-800/8">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="coberturaBarClass"
          :style="{ width: coberturaWidth }"
        />
      </div>
      <p class="mt-1.5 text-sm font-semibold text-navy-800">
        Cobertura {{ center.cobertura }}%
      </p>
    </div>

    <BaseButton
      variant="navy"
      full-width
      class="mt-4"
      :disabled="isCerrado"
      @click="emit('select', center.id)"
    >
      {{ isCerrado ? 'Cerrado' : 'Donar aquí' }}
    </BaseButton>
  </article>
</template>
