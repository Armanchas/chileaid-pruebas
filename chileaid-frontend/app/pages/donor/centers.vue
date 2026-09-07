<script setup lang="ts">
/**
 * PÁGINA — Listado completo de centros de acopio. Solo orquesta: toma el
 * ViewModel, carga los datos y reparte estado/acciones a la vista vía
 * props/eventos. Sin lógica de negocio ni datos.
 */
import { useCentersViewModel } from '~/composables/useCentersViewModel'
import CentersView from '~/components/donor/CentersView.vue'
import { REGIONES_CHILE } from '~/services/donorDashboardService'

definePageMeta({ layout: 'donor', middleware: 'auth-donor' })

const {
  filteredCenters,
  filters,
  emergenciaNombre,
  isLoading,
  error,
  totalVisible,
  loadCenters,
  setRegion,
  setTipoEmergencia,
  clearEmergencia,
  resetFilters
} = useCentersViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadCenters()
</script>

<template>
  <CentersView
    :centers="filteredCenters"
    :is-loading="isLoading"
    :error="error"
    :selected-region="filters.region"
    :selected-tipo="filters.tipoEmergencia"
    :emergencia-nombre="emergenciaNombre"
    :total-visible="totalVisible"
    :regiones="REGIONES_CHILE"
    @region-change="setRegion"
    @tipo-change="setTipoEmergencia"
    @clear-emergencia="clearEmergencia"
    @reset-filters="resetFilters"
    @select-center="(id) => navigateTo('/donor/center/' + id)"
  />
</template>
