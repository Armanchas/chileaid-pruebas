<script setup lang="ts">
/**
 * PÁGINA — Historial de donaciones. Solo orquesta: toma el ViewModel, carga las
 * donaciones y reparte estado/acciones a la vista vía props/eventos. Sin lógica
 * de negocio ni datos inline.
 */
import { useTrackingViewModel } from '~/composables/useTrackingViewModel'
import TrackingView from '~/components/donor/TrackingView.vue'

definePageMeta({ layout: 'donor', middleware: 'auth-donor' })

const {
  donations,
  total,
  isLoading,
  error,
  activeQRCode,
  currentPage,
  cancellingId,
  totalPages,
  hasNextPage,
  hasPrevPage,
  loadDonations,
  nextPage,
  prevPage,
  cancelDonation,
  openQR,
  closeQR,
  goProfile
} = useTrackingViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadDonations()
</script>

<template>
  <TrackingView
    :donations="donations"
    :total="total"
    :is-loading="isLoading"
    :error="error"
    :active-q-r-code="activeQRCode"
    :current-page="currentPage"
    :total-pages="totalPages"
    :has-next-page="hasNextPage"
    :has-prev-page="hasPrevPage"
    :cancelling-id="cancellingId"
    @next-page="nextPage"
    @prev-page="prevPage"
    @cancel="cancelDonation"
    @open-qr="openQR"
    @close-qr="closeQR"
    @go-profile="goProfile"
  />
</template>
