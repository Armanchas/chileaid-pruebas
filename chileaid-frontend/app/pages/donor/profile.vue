<script setup lang="ts">
/**
 * PÁGINA — Perfil del donante. Solo orquesta: toma el ViewModel, carga el perfil
 * y reparte estado/acciones a la vista vía props/eventos. Sin lógica de negocio
 * ni datos inline.
 */
import { useProfileViewModel } from '~/composables/useProfileViewModel'
import ProfileView from '~/components/donor/ProfileView.vue'

definePageMeta({ layout: 'donor', middleware: 'auth-donor' })

const {
  profile,
  totalDonaciones,
  form,
  isSaving,
  saveSuccess,
  saveError,
  isLoading,
  error,
  activeQRCode,
  recentDonations,
  loadProfile,
  saveProfile,
  openQR,
  closeQR,
  goBack
} = useProfileViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadProfile()

/** Refleja en el formulario reactivo el campo editado en la vista. */
function setField(field: 'nombre' | 'apellido' | 'email', value: string): void {
  form.value[field] = value
}
</script>

<template>
  <ProfileView
    :profile="profile"
    :total-donaciones="totalDonaciones"
    :form="form"
    :is-saving="isSaving"
    :save-success="saveSuccess"
    :save-error="saveError"
    :is-loading="isLoading"
    :error="error"
    :active-q-r-code="activeQRCode"
    :recent-donations="recentDonations"
    @update:form="setField"
    @save="saveProfile"
    @open-qr="openQR"
    @close-qr="closeQR"
    @go-back="goBack"
    @go-tracking="() => navigateTo('/donor/tracking')"
  />
</template>
