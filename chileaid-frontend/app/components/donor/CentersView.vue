<script setup lang="ts">
import { computed } from 'vue'
import CenterFilters from '~/components/donor/CenterFilters.vue'
import DonorCenterCard from '~/components/donor/DonorCenterCard.vue'
import type { CenterDTO } from '~/services/donorCentersService'

/**
 * VIEW — Orquesta el listado completo de centros. Puramente visual: recibe todo
 * por props y reparte a los filtros y tarjetas, comunicando intenciones por
 * eventos. No conoce servicios ni composables.
 */
type TipoFiltro = 'todas' | 'terremoto' | 'incendio' | 'aluvion' | 'otro'

const props = defineProps<{
  centers: CenterDTO[]
  isLoading: boolean
  error: string | null
  selectedRegion: string
  selectedTipo: TipoFiltro
  emergenciaNombre: string | null
  totalVisible: number
  regiones: string[]
}>()

const emit = defineEmits<{
  'region-change': [region: string]
  'tipo-change': [tipo: TipoFiltro]
  'clear-emergencia': []
  'reset-filters': []
  'select-center': [id: string]
}>()

/** Verdadero si la combinación de filtros deja al menos un centro visible. */
const hasResults = computed(() => props.centers.length > 0)
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
    <!-- 1. Header de sección -->
    <header>
      <h1 class="font-display text-2xl font-black uppercase text-navy-800">
        Centros de acopio
      </h1>
      <p class="mt-1 text-slate-500">
        Encuentra el centro más cercano y dona lo que más se necesita
      </p>
    </header>

    <!-- Banner: filtrando por una emergencia concreta (llegada desde el dashboard) -->
    <div
      v-if="emergenciaNombre"
      class="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl bg-navy-800/8 px-4 py-3"
    >
      <p class="text-sm font-semibold text-navy-800">
        Mostrando centros de:
        <span class="font-black uppercase">{{ emergenciaNombre }}</span>
      </p>
      <button
        type="button"
        class="text-sm font-semibold text-navy-600 underline hover:text-navy-800"
        @click="emit('clear-emergencia')"
      >
        Ver todos los centros
      </button>
    </div>

    <!-- 2. Filtros -->
    <div class="mt-6">
      <CenterFilters
        :selected-region="selectedRegion"
        :selected-tipo="selectedTipo"
        :total-visible="totalVisible"
        :regiones="regiones"
        @region-change="(region) => emit('region-change', region)"
        @tipo-change="(tipo) => emit('tipo-change', tipo)"
        @reset="emit('reset-filters')"
      />
    </div>

    <!-- 6. Estado error -->
    <p
      v-if="error"
      role="alert"
      class="rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
    >
      {{ error }}
    </p>

    <!-- 5. Estado loading: skeletons -->
    <div
      v-else-if="isLoading"
      class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3"
    >
      <div
        v-for="n in 6"
        :key="n"
        class="h-48 animate-pulse rounded-2xl bg-navy-800/6"
      />
    </div>

    <!-- 3. Grid de centros -->
    <div
      v-else-if="hasResults"
      class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3"
    >
      <DonorCenterCard
        v-for="center in centers"
        :key="center.id"
        :center="center"
        @select="(id) => emit('select-center', id)"
      />
    </div>

    <!-- 4. Estado vacío -->
    <div
      v-else
      class="flex flex-col items-center justify-center rounded-2xl border border-navy-800/10 py-16 text-center"
    >
      <svg
        class="h-10 w-10 text-slate-400"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="M21 21l-4.3-4.3" />
      </svg>
      <p class="mt-3 max-w-xs text-slate-400">
        No hay centros que coincidan con los filtros seleccionados
      </p>
      <button
        type="button"
        class="mt-4 text-sm font-semibold text-navy-600 underline hover:text-navy-800"
        @click="emit('reset-filters')"
      >
        Ver todos los centros
      </button>
    </div>
  </div>
</template>
