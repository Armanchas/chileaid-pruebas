<script setup lang="ts">
/**
 * PÁGINA — Panel de inicio del donante. Solo orquesta: toma el ViewModel,
 * carga los datos y reparte estado/acciones a la vista vía props/eventos.
 * Sin lógica de negocio ni datos.
 */
import { useDonorDashboardViewModel } from '~/composables/useDonorDashboardViewModel'
import DonorDashboardView from '~/components/donor/DonorDashboardView.vue'

definePageMeta({ layout: 'donor', middleware: 'auth-donor' })

const {
  emergencies,
  criticalCenters,
  isLoading,
  error,
  loadDashboard
} = useDonorDashboardViewModel()

// Nombre del donante: fallback hasta cablear la sesión autenticada.
const userName = 'Donante'

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadDashboard()
</script>

<template>
  <DonorDashboardView
    :emergencies="emergencies"
    :critical-centers="criticalCenters"
    :is-loading="isLoading"
    :error="error"
    :user-name="userName"
    @select-emergency="(emergency) => navigateTo({
      path: '/donor/centers',
      query: {
        emergenciaId: emergency.id,
        emergenciaNombre: emergency.nombre
      }
    })"
    @select-center="(id) => navigateTo('/donor/center/' + id)"
  />
</template>
