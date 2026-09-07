<script setup lang="ts">
/**
 * PÁGINA — Solo orquesta. Toma el ViewModel de registro de organización (CU-01)
 * y reparte su estado y acciones al formulario vía props/eventos. Pasa el
 * catálogo de regiones como prop (el componente no toca services). Sin lógica de
 * negocio ni datos.
 */
import { useOrgRegisterViewModel } from '~/composables/useOrgRegisterViewModel'
import OrgRegisterForm from '~/components/auth/OrgRegisterForm.vue'
import { REGIONES_CHILE } from '~/services/donorDashboardService'

const {
  form,
  documentFile,
  errors,
  touched,
  isLoading,
  submitError,
  isFormValid,
  onFieldTouch,
  onUpdateModel,
  onDocumentChange,
  submit
} = useOrgRegisterViewModel()
</script>

<template>
  <main class="flex min-h-screen flex-col bg-[#f0f4ff] px-4 py-12">
    <div class="mx-auto flex w-full max-w-2xl flex-col items-center">
      <!-- Badge -->
      <NuxtLink
        to="/"
        class="mb-6 inline-flex items-center gap-2 rounded-full bg-alert px-4 py-1.5
               font-display text-sm font-bold uppercase tracking-widest text-white"
      >
        <span class="h-2 w-2 rounded-full bg-white" />
        Chile Aid
      </NuxtLink>

      <!-- Título + subtítulo -->
      <h1 class="text-center font-display text-3xl font-black uppercase text-navy-800 sm:text-4xl">
        Registrar Organización
      </h1>
      <p class="mt-2 max-w-lg text-center text-slate-500">
        Únete a la red de respuesta regional. Las organizaciones verificadas
        reciben acceso prioritario a la plataforma.
      </p>

      <!-- Formulario -->
      <div class="mt-8 w-full">
        <OrgRegisterForm
          :model-value="form"
          :document-file="documentFile"
          :errors="errors"
          :touched="touched"
          :is-loading="isLoading"
          :submit-error="submitError"
          :is-form-valid="isFormValid"
          :regiones="REGIONES_CHILE"
          @update:model-value="({ field, value }) => onUpdateModel(field, value)"
          @document-change="onDocumentChange"
          @submit="submit"
          @field-touch="onFieldTouch"
        />
      </div>

      <!-- Acceso a login -->
      <p class="mt-8 text-center text-navy-600">
        ¿Ya tienes cuenta?
        <NuxtLink
          to="/login"
          class="font-display font-bold uppercase tracking-widest text-navy-800
                 underline-offset-4 transition-colors hover:text-navy-600 hover:underline"
        >
          Ingresar
        </NuxtLink>
      </p>
    </div>
  </main>
</template>
