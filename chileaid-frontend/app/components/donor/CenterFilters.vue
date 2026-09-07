<script setup lang="ts">
import { computed } from 'vue'

/**
 * VIEW — Barra de filtros del listado de centros. Puramente visual: recibe el
 * estado seleccionado por props y emite la intención de cambio hacia arriba.
 * No conoce servicios ni composables; el mapeo tipo→color es presentación.
 */
type TipoFiltro = 'todas' | 'terremoto' | 'incendio' | 'aluvion' | 'otro'

const props = defineProps<{
  selectedRegion: string
  selectedTipo: TipoFiltro
  totalVisible: number
  regiones: string[]
}>()

const emit = defineEmits<{
  'region-change': [region: string]
  'tipo-change': [tipo: TipoFiltro]
  reset: []
}>()

/** Pills de tipo de emergencia: valor, etiqueta y clases activo/inactivo. */
const TIPOS: { value: TipoFiltro; label: string; active: string }[] = [
  { value: 'todas', label: 'Todas', active: 'bg-navy-800 text-white' },
  { value: 'terremoto', label: 'Terremoto', active: 'bg-red-100 text-red-800 border border-red-200' },
  { value: 'incendio', label: 'Incendio', active: 'bg-orange-100 text-orange-800 border border-orange-200' },
  { value: 'aluvion', label: 'Aluvión', active: 'bg-blue-100 text-blue-800 border border-blue-200' },
  { value: 'otro', label: 'Otro', active: 'bg-slate-100 text-slate-700 border border-slate-200' }
]

const INACTIVE_PILL = 'bg-white/60 border border-navy-800/15 text-navy-600'

/** Hay algún filtro activo distinto del estado neutro. */
const hasActiveFilters = computed(
  () =>
    props.selectedRegion !== 'Todas las regiones' ||
    props.selectedTipo !== 'todas'
)

function onRegionChange(event: Event) {
  emit('region-change', (event.target as HTMLSelectElement).value)
}
</script>

<template>
  <div class="glass-auth mb-8 rounded-2xl px-4 py-3">
    <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <!-- Selector de región -->
      <div class="lg:shrink-0">
        <label
          class="mb-1 block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
        >
          Región
        </label>
        <select
          :value="selectedRegion"
          class="w-full rounded-lg border border-navy-800/15 bg-white/80 px-3 py-2 text-navy-800
                 focus:outline-none focus-visible:ring-2 focus-visible:ring-navy-600/40 lg:w-64"
          @change="onRegionChange"
        >
          <option v-for="region in regiones" :key="region" :value="region">
            {{ region }}
          </option>
        </select>
      </div>

      <!-- Pills de tipo de emergencia -->
      <div class="lg:min-w-0 lg:flex-1">
        <span
          class="mb-1 block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
        >
          Tipo de emergencia
        </span>
        <div class="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1 lg:flex-wrap lg:overflow-visible">
          <button
            v-for="tipo in TIPOS"
            :key="tipo.value"
            type="button"
            class="shrink-0 rounded-full px-3 py-1.5 font-display text-sm font-bold uppercase tracking-wide
                   transition-colors duration-150"
            :class="selectedTipo === tipo.value ? tipo.active : INACTIVE_PILL"
            @click="emit('tipo-change', tipo.value)"
          >
            {{ tipo.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Conteo + limpiar -->
    <div class="mt-2 flex items-center justify-between gap-3">
      <p class="text-sm text-slate-500">
        Mostrando {{ totalVisible }}
        {{ totalVisible === 1 ? 'centro' : 'centros' }}
      </p>
      <button
        v-if="hasActiveFilters"
        type="button"
        class="text-sm text-navy-600 underline hover:text-navy-800"
        @click="emit('reset')"
      >
        Limpiar filtros
      </button>
    </div>
  </div>
</template>
