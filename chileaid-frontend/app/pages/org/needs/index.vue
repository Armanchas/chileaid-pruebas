<script setup lang="ts">
/**
 * PÁGINA — Gestión de necesidades de la organización receptora. Orquesta el
 * ViewModel y reparte estado/acciones a las vistas vía props/eventos. Cero lógica
 * de negocio: todo fluye Service → Composable → Vista.
 */
import { useOrgNeedsViewModel } from '~/composables/useOrgNeedsViewModel'
import OrgNeedsView from '~/components/org/needs/OrgNeedsView.vue'
import OrgNeedFormModal from '~/components/org/needs/OrgNeedFormModal.vue'

definePageMeta({ layout: 'org', middleware: 'auth-org' })

const {
  needs,
  catalog,
  isLoading,
  showFormModal,
  selectedNeed,
  isSubmitting,
  submitError,
  closingId,
  loadData,
  openCreateModal,
  openEditModal,
  closeFormModal,
  submitForm,
  closeNeed
} = useOrgNeedsViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadData()
</script>

<template>
  <div>
    <OrgNeedsView
      :needs="needs"
      :is-loading="isLoading"
      :closing-id="closingId"
      @open-create="openCreateModal"
      @edit-need="openEditModal"
      @close-need="closeNeed"
    />

    <OrgNeedFormModal
      :is-open="showFormModal"
      :catalog="catalog"
      :initial-data="selectedNeed"
      :is-submitting="isSubmitting"
      :submit-error="submitError"
      @close="closeFormModal"
      @submit="submitForm"
    />
  </div>
</template>
