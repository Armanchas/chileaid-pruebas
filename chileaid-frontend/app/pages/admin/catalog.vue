<script setup lang="ts">
/**
 * PÁGINA — Gestión del catálogo de insumos del administrador. Orquesta el
 * ViewModel y reparte estado/acciones a la vista y al modal vía props/eventos.
 * Cero lógica de negocio.
 */
import { useAdminCatalogViewModel } from '~/composables/useAdminCatalogViewModel'
import AdminCatalogView from '~/components/admin/AdminCatalogView.vue'
import AdminCreateInsumoModal from '~/components/admin/AdminCreateInsumoModal.vue'

definePageMeta({ layout: 'admin', middleware: 'auth-admin' })

const {
  isLoading,
  error,
  showCreateModal,
  deletingId,
  submitError,
  isSubmitting,
  searchQuery,
  selectedCategoria,
  catalogFiltrado,
  categoriasCounts,
  loadCatalog,
  openCreateModal,
  closeCreateModal,
  submitCreate,
  deleteInsumo,
  setSearch,
  setCategoria
} = useAdminCatalogViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadCatalog()
</script>

<template>
  <AdminCatalogView
    :catalog="catalogFiltrado"
    :is-loading="isLoading"
    :error="error"
    :deleting-id="deletingId"
    :search-query="searchQuery"
    :selected-categoria="selectedCategoria"
    :categorias-counts="categoriasCounts"
    @open-create="openCreateModal"
    @delete-insumo="deleteInsumo"
    @update:search="setSearch"
    @set-categoria="setCategoria"
  />

  <AdminCreateInsumoModal
    :is-open="showCreateModal"
    :submit-error="submitError"
    :is-submitting="isSubmitting"
    @close="closeCreateModal"
    @submit="submitCreate"
  />
</template>
