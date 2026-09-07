<script setup lang="ts">
/**
 * PÁGINA — Panel de inicio de la organización receptora. Orquesta el ViewModel y
 * reparte estado/acciones a la vista vía props/eventos. Cero lógica de negocio.
 *
 * Las recepciones (CU-07) viven en `/org/receptions`; el dashboard solo enlaza
 * a esa pantalla (`go-receptions` → `goToReceptions`).
 */
import { useOrgDashboardViewModel } from '~/composables/useOrgDashboardViewModel'
import OrgDashboardView from '~/components/org/OrgDashboardView.vue'

definePageMeta({ layout: 'org', middleware: 'auth-org' })

const {
  center,
  activeNeeds,
  urgentNeedsCount,
  hasCenter,
  coberturaColor,
  isLoading,
  error,
  showCenterForm,
  centerFormMode,
  isSavingCenter,
  centerFormError,
  centerFormDefaults,
  activeEmergencies,
  loadDashboard,
  openCenterForm,
  openEditCenterForm,
  closeCenterForm,
  submitCenter,
  geocodeAddress,
  goToNeeds,
  goToReceptions
} = useOrgDashboardViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadDashboard()
</script>

<template>
  <OrgDashboardView
    :center="center"
    :active-needs="activeNeeds"
    :urgent-needs-count="urgentNeedsCount"
    :has-center="hasCenter"
    :cobertura-color="coberturaColor"
    :is-loading="isLoading"
    :error="error"
    :center-form-defaults="centerFormDefaults"
    :active-emergencies="activeEmergencies"
    :show-center-form="showCenterForm"
    :center-form-mode="centerFormMode"
    :is-saving-center="isSavingCenter"
    :center-form-error="centerFormError"
    :geocode="geocodeAddress"
    @manage-needs="goToNeeds"
    @go-receptions="goToReceptions"
    @open-center-form="openCenterForm"
    @open-edit-center-form="openEditCenterForm"
    @close-center-form="closeCenterForm"
    @submit-center="submitCenter"
  />
</template>
