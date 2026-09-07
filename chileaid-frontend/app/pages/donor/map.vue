<script setup lang="ts">
/**
 * PÁGINA — Mapa interactivo de centros. Solo orquesta: toma el ViewModel, carga
 * los centros y reparte estado/acciones a la vista vía props/eventos. Sin lógica
 * de negocio ni datos inline.
 */
import { useMapViewModel } from '~/composables/useMapViewModel'
import MapView from '~/components/donor/MapView.vue'

definePageMeta({ layout: 'donor', middleware: 'auth-donor' })

const route = useRoute()
const initialCenterId = route.query.center as string | undefined

const {
  centers,
  selectedCenter,
  isLoading,
  error,
  loadCenters,
  selectCenter,
  clearSelection,
  goToCenter,
  donate,
  goBack
} = useMapViewModel({ initialCenterId })

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadCenters()
</script>

<template>
  <MapView
    :centers="centers"
    :selected-center="selectedCenter"
    :is-loading="isLoading"
    :error="error"
    @select-center="selectCenter"
    @clear-selection="clearSelection"
    @go-to-center="goToCenter"
    @donate="donate"
    @go-back="goBack"
  />
</template>
