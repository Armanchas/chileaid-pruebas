<script setup lang="ts">
import { computed } from 'vue'
import type { NeedDTO } from '~/services/donorCentersService'

/**
 * VIEW — Tarjeta destacada de una necesidad urgente. Puramente visual: recibe
 * el DTO por prop y muestra su cobertura. El mapeo cobertura→color es
 * presentación. La acción de donar vive a nivel de centro, no por ítem.
 */
const props = defineProps<{
  need: NeedDTO
}>()

/** Clase Tailwind de la barra según la cobertura del ítem. */
const coberturaBarClass = computed(() => {
  if (props.need.cobertura >= 70) return 'bg-green-500'
  if (props.need.cobertura >= 30) return 'bg-amber-400'
  return 'bg-red-500'
})

/** Color hex del borde izquierdo (border-l-3 no existe en Tailwind). */
const borderColor = computed(() => {
  if (props.need.cobertura >= 70) return '#22c55e'
  if (props.need.cobertura >= 30) return '#fbbf24'
  return '#ef4444'
})

const coberturaWidth = computed(
  () => `${Math.min(100, Math.max(0, props.need.cobertura))}%`
)

/** Estilo de borde izquierdo solo para los ítems marcados como urgentes. */
const cardStyle = computed(() =>
  props.need.urgente ? { borderLeft: `3px solid ${borderColor.value}` } : {}
)
</script>

<template>
  <article
    class="glass-auth flex flex-col rounded-2xl p-6 transition-all duration-200
           hover:-translate-y-0.5 hover:shadow-lg hover:shadow-navy-800/10"
    :style="cardStyle"
  >
    <p class="text-xs uppercase tracking-widest text-slate-500">
      {{ need.categoria }}
    </p>
    <h3 class="mt-1 font-display text-xl font-black uppercase leading-tight text-navy-800">
      {{ need.nombre }}
    </h3>
    <p class="mt-1 text-sm text-slate-500">
      Requeridos: {{ need.cantidadRequerida }} {{ need.unidad }}
    </p>

    <!-- Barra de cobertura del ítem -->
    <div class="mt-4">
      <div class="h-2 w-full overflow-hidden rounded-full bg-navy-800/8">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="coberturaBarClass"
          :style="{ width: coberturaWidth }"
        />
      </div>
      <p class="mt-1.5 text-sm font-semibold text-navy-800">
        Cobertura {{ need.cobertura }}%
      </p>
    </div>
  </article>
</template>
