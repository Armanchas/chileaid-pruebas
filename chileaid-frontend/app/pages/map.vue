<script setup lang="ts">
/**
 * PÁGINA PÚBLICA — Mapa de centros accesible sin sesión (§3.1 del plan). Un
 * visitante anónimo puede ver dónde donar; el login se difiere al momento de
 * donar (al navegar a `/donor/donate/:id` el middleware `auth-donor` desvía a
 * `/login?redirect=...` y devuelve al flujo tras autenticar).
 *
 * Reutiliza la MISMA vista (`MapView`) y ViewModel (`useMapViewModel`) del mapa
 * del donante; la única diferencia es `backTo: '/'` (vuelve a la landing) y que
 * esta ruta NO lleva `middleware` ni `layout` (los datos de `GET /centers` son
 * públicos). Sin layout renderiza standalone, como `/` y `/login`.
 */
import { useMapViewModel } from '~/composables/useMapViewModel'
import MapView from '~/components/donor/MapView.vue'

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
} = useMapViewModel({ initialCenterId, backTo: '/' })

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
