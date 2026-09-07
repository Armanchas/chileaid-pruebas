<script setup lang="ts">
/**
 * PÁGINA — Flujo de donación a un centro. Solo orquesta: toma el ViewModel del
 * centro de la ruta, carga sus datos y reparte estado/acciones a la vista vía
 * props/eventos. Sin lógica de negocio ni datos inline.
 */
import { useDonationViewModel } from '~/composables/useDonationViewModel'
import DonationView from '~/components/donor/DonationView.vue'

definePageMeta({ layout: 'donor', middleware: 'auth-donor' })

const route = useRoute()
const centerId = route.params.centerId as string

const {
  center,
  donation,
  quantities,
  canSubmit,
  hasSelection,
  isLoading,
  isSubmitting,
  submitted,
  error,
  loadCenter,
  submitDonation,
  goBack,
  goTracking
} = useDonationViewModel(centerId)

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadCenter()

/** Refleja en el mapa reactivo la cantidad que ingresa la vista. */
function setQuantity(needId: string, value: number): void {
  quantities.value[needId] = value
}
</script>

<template>
  <DonationView
    :center="center"
    :donation="donation"
    :quantities="quantities"
    :can-submit="canSubmit"
    :has-selection="hasSelection"
    :is-loading="isLoading"
    :is-submitting="isSubmitting"
    :submitted="submitted"
    :error="error"
    @update:quantities="setQuantity"
    @submit="submitDonation"
    @go-back="goBack"
    @go-tracking="goTracking"
  />
</template>
