<script setup lang="ts">
/**
 * PÁGINA — Gestión de emergencias del administrador. Orquesta el ViewModel y
 * reparte estado/acciones a la vista y al modal vía props/eventos. Cero lógica
 * de negocio.
 */
import { useAdminEmergenciesViewModel } from '~/composables/useAdminEmergenciesViewModel'
import AdminEmergenciesView from '~/components/admin/AdminEmergenciesView.vue'
import AdminCreateEmergencyModal from '~/components/admin/AdminCreateEmergencyModal.vue'

definePageMeta({ layout: 'admin', middleware: 'auth-admin' })

const {
  isLoading,
  error,
  showCreateModal,
  submitError,
  isSubmitting,
  closingId,
  selectedEstado,
  emergenciesFiltradas,
  estadoCounts,
  loadEmergencies,
  openCreateModal,
  closeCreateModal,
  submitCreate,
  closeEmergency,
  setEstado
} = useAdminEmergenciesViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadEmergencies()
</script>

<template>
  <AdminEmergenciesView
    :emergencies="emergenciesFiltradas"
    :is-loading="isLoading"
    :error="error"
    :closing-id="closingId"
    :selected-estado="selectedEstado"
    :estado-counts="estadoCounts"
    @open-create="openCreateModal"
    @close-emergency="closeEmergency"
    @set-estado="setEstado"
  />

  <AdminCreateEmergencyModal
    :is-open="showCreateModal"
    :submit-error="submitError"
    :is-submitting="isSubmitting"
    @close="closeCreateModal"
    @submit="submitCreate"
  />
</template>
