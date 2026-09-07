<script setup lang="ts">
/**
 * PÁGINA — Distribución de inventario de la organización receptora. Orquesta el
 * ViewModel y reparte estado/acciones a las vistas vía props/eventos. Cero lógica
 * de negocio: todo fluye Service → Composable → Vista.
 *
 * Las salidas disponibles dependen del tipo de centro: la página deriva la lista
 * con `accionesDisponibles(orgTipo)` del composable y la pasa al modal (así el
 * componente no importa lógica de dominio).
 */
import { useDistributionViewModel } from '~/composables/useDistributionViewModel'
import OrgDistributionView from '~/components/org/distribution/OrgDistributionView.vue'
import OrgCreateLotModal from '~/components/org/distribution/OrgCreateLotModal.vue'

definePageMeta({ layout: 'org', middleware: 'auth-org' })

const {
  lots,
  stock,
  isLoading,
  submitError,
  showCreateModal,
  totalDistribuido,
  availableActions,
  loadData,
  openCreateModal,
  closeCreateModal,
  submitLot
} = useDistributionViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly). El tipo de
// centro (que decide `availableActions`) se deriva del perfil dentro del VM.
await loadData()
</script>

<template>
  <div>
    <OrgDistributionView
      :lots="lots"
      :stock="stock"
      :is-loading="isLoading"
      :total-distribuido="totalDistribuido"
      @open-create="openCreateModal"
    />

    <OrgCreateLotModal
      :is-open="showCreateModal"
      :stock="stock"
      :available-actions="availableActions"
      :submit-error="submitError"
      @close="closeCreateModal"
      @submit="submitLot"
    />
  </div>
</template>
