<script setup lang="ts">
/**
 * PÁGINA — Confirmación de recepciones de la organización (CU-07). Orquesta el
 * ViewModel y reparte estado/acciones a la vista vía props/eventos. Cero lógica
 * de negocio: todo fluye Service → Composable → Vista.
 */
import { useOrgReceptionsViewModel } from '~/composables/useOrgReceptionsViewModel'
import OrgReceptionsView from '~/components/org/OrgReceptionsView.vue'

definePageMeta({ layout: 'org', middleware: 'auth-org' })

const {
  pendingReceptions,
  isLoading,
  error,
  receptionCode,
  isConfirming,
  confirmError,
  confirmSuccess,
  hasPendingReceptions,
  loadReceptions,
  setReceptionCode,
  confirmReception,
  goBack
} = useOrgReceptionsViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadReceptions()
</script>

<template>
  <OrgReceptionsView
    :pending-receptions="pendingReceptions"
    :is-loading="isLoading"
    :error="error"
    :reception-code="receptionCode"
    :is-confirming="isConfirming"
    :confirm-error="confirmError"
    :confirm-success="confirmSuccess"
    :has-pending-receptions="hasPendingReceptions"
    @update:reception-code="setReceptionCode"
    @confirm-reception="(codigo) => confirmReception(codigo)"
    @go-back="goBack"
  />
</template>
