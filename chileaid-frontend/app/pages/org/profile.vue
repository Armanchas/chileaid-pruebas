<script setup lang="ts">
/**
 * PÁGINA — Perfil de la organización. Solo orquesta: toma el ViewModel, carga el
 * perfil y reparte estado/acciones a la vista vía props/eventos. Sin lógica de
 * negocio ni datos inline.
 */
import { useOrgProfileViewModel } from '~/composables/useOrgProfileViewModel'
import OrgProfileView from '~/components/org/OrgProfileView.vue'
import { REGIONES_CHILE } from '~/services/donorDashboardService'

definePageMeta({ layout: 'org', middleware: 'auth-org' })

const {
  profile,
  form,
  isLoading,
  error,
  isSaving,
  saveError,
  saveSuccess,
  labelTipo,
  labelEstado,
  colorEstado,
  isFormDirty,
  loadProfile,
  saveProfile,
  resetForm,
  goBack
} = useOrgProfileViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadProfile()

/** Refleja en el formulario reactivo el campo editado en la vista. */
function setField(
  field: 'contactoNombre' | 'email' | 'telefono' | 'region',
  value: string
): void {
  form[field] = value
}
</script>

<template>
  <OrgProfileView
    :profile="profile"
    :form="form"
    :is-loading="isLoading"
    :is-saving="isSaving"
    :error="error"
    :save-error="saveError"
    :save-success="saveSuccess"
    :label-tipo="labelTipo"
    :label-estado="labelEstado"
    :color-estado="colorEstado"
    :is-form-dirty="isFormDirty"
    :regiones="REGIONES_CHILE"
    @update:form="setField"
    @save="saveProfile"
    @reset="resetForm"
    @go-back="goBack"
  />
</template>
