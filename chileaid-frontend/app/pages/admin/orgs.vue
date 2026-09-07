<script setup lang="ts">
/**
 * PÁGINA — Gestión de organizaciones del administrador. Orquesta el ViewModel y
 * reparte estado/acciones a la vista vía props/eventos. Cero lógica de negocio.
 */
import { useAdminOrgsViewModel } from '~/composables/useAdminOrgsViewModel'
import AdminOrgsView from '~/components/admin/AdminOrgsView.vue'
import type { OrgEstado } from '~/services/orgProfileService'

definePageMeta({ layout: 'admin', middleware: 'auth-admin' })

const {
  orgs,
  filtroEstado,
  isLoading,
  error,
  actionLoadingId,
  actionError,
  selectedOrg,
  selectedOrgDocuments,
  isLoadingDocuments,
  conteosPorEstado,
  currentPage,
  totalPages,
  hasNextPage,
  hasPrevPage,
  loadOrgs,
  setFiltro,
  nextPage,
  prevPage,
  selectOrg,
  clearSelection,
  approveOrg,
  rejectOrg,
  deactivateOrg,
  reactivateOrg
} = useAdminOrgsViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadOrgs()
</script>

<template>
  <AdminOrgsView
    :orgs="orgs"
    :is-loading="isLoading"
    :error="error"
    :filtro-estado="filtroEstado"
    :conteos-por-estado="conteosPorEstado"
    :current-page="currentPage"
    :total-pages="totalPages"
    :has-next-page="hasNextPage"
    :has-prev-page="hasPrevPage"
    :action-loading-id="actionLoadingId"
    :action-error="actionError"
    :selected-org="selectedOrg"
    :selected-org-documents="selectedOrgDocuments"
    :is-loading-documents="isLoadingDocuments"
    @set-filtro="(estado) => setFiltro(estado as OrgEstado | 'todas')"
    @next-page="nextPage"
    @prev-page="prevPage"
    @select-org="selectOrg"
    @clear-selection="clearSelection"
    @approve="approveOrg"
    @reject="rejectOrg"
    @deactivate="deactivateOrg"
    @reactivate="reactivateOrg"
  />
</template>
