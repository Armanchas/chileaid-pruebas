<script setup lang="ts">
import { computed } from 'vue'
import type { NeedDTO } from '~/services/donorCentersService'

/**
 * VIEW — Fila compacta de una necesidad (lista "Otras / Completadas").
 * Puramente visual: recibe el DTO por prop y muestra su cobertura/estado. El
 * mapeo cobertura→color es presentación. Donar es una acción a nivel de centro.
 */
const props = defineProps<{
  need: NeedDTO
}>()

const isCompleted = computed(() => props.need.estado === 'completada')

/** Inicial de la categoría para el ícono circular. */
const inicial = computed(() => props.need.categoria.charAt(0).toUpperCase())

/** Color del badge de cobertura según el porcentaje cubierto. */
const coberturaBadgeClass = computed(() => {
  if (props.need.cobertura >= 70) return 'bg-green-100 text-green-700'
  if (props.need.cobertura >= 30) return 'bg-amber-100 text-amber-700'
  return 'bg-red-100 text-red-600'
})
</script>

<template>
  <div class="flex items-center gap-3 border-b border-navy-800/8 py-3 last:border-b-0">
    <!-- Ícono de categoría -->
    <span
      class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full
             bg-navy-800/8 font-display text-sm font-bold text-navy-700"
      aria-hidden="true"
    >
      {{ inicial }}
    </span>

    <!-- Nombre + unidad -->
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-semibold text-navy-800">
        {{ need.nombre }}
      </p>
      <p class="truncate text-sm text-slate-500">
        {{ need.cantidadRequerida }} {{ need.unidad }} · {{ need.categoria }}
      </p>
    </div>

    <!-- Badge de cobertura -->
    <span
      class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold"
      :class="coberturaBadgeClass"
    >
      Cubierto {{ need.cobertura }}%
    </span>

    <!-- Estado -->
    <span
      v-if="isCompleted"
      class="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-500"
    >
      Meta alcanzada
    </span>
  </div>
</template>
