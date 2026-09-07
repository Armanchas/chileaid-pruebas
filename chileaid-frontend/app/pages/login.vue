<script setup lang="ts">
/**
 * PÁGINA — Solo orquesta. Toma el ViewModel de login y reparte su estado y
 * acciones al formulario vía props/eventos. Sin lógica de negocio ni datos.
 */
import { useLoginViewModel } from '~/composables/useLoginViewModel'
import LoginForm from '~/components/auth/LoginForm.vue'

const {
  email,
  password,
  isLoading,
  error,
  isFormValid,
  onSubmit,
  onDonorAccess,
  onOrgAccess
} = useLoginViewModel()

// Aviso al volver del registro de organización (CU-01): la solicitud queda
// pendiente de verificación. La navegación la decide el ViewModel del registro.
const route = useRoute()
const registeredOrg = computed(() => route.query.registered === 'org')
// El registro sube el documento de respaldo en el mismo flujo; si esa subida
// falla (ej. red), `useOrgRegisterViewModel.submit` igual crea la cuenta y
// navega aquí con `docPending=1` para avisar que falta subirlo desde el perfil.
const docPending = computed(() => route.query.docPending === '1')
</script>

<template>
  <main
    class="relative flex min-h-screen items-center justify-center overflow-hidden
           bg-[#f0f4ff] px-4 py-16"
  >
    <!-- Resplandor de fondo sutil -->
    <div
      class="pointer-events-none absolute -left-40 top-1/4 h-96 w-96 rounded-full bg-navy-800/8 blur-3xl"
      aria-hidden="true"
    />
    <div
      class="pointer-events-none absolute -right-32 bottom-0 h-96 w-96 rounded-full bg-alert/8 blur-3xl"
      aria-hidden="true"
    />

    <div class="relative flex w-full max-w-md flex-col items-center">
      <!-- Badge superior estilo HeroSection -->
      <NuxtLink
        to="/"
        class="alert-pulse mb-8 inline-flex items-center gap-2 rounded-full bg-alert px-4 py-1.5
               font-display text-sm font-bold uppercase tracking-widest text-white"
      >
        <span class="h-2 w-2 rounded-full bg-white" />
        Chile Aid
      </NuxtLink>

      <!-- Aviso: solicitud de organización recibida (pendiente de verificación) -->
      <div
        v-if="registeredOrg"
        role="status"
        class="glass-auth mb-6 w-full max-w-md rounded-xl border-l-4 border-navy-600 px-4 py-3 text-navy-800"
      >
        <span class="font-semibold">✓ Solicitud recibida</span> — Tu organización
        quedará activa una vez que el equipo de Chile Aid verifique la
        documentación enviada.
      </div>

      <!-- Aviso: la cuenta se creó pero el documento no se pudo subir -->
      <div
        v-if="registeredOrg && docPending"
        role="alert"
        class="glass-auth mb-6 w-full max-w-md rounded-xl border-l-4 border-alert px-4 py-3 text-navy-800"
      >
        <span class="font-semibold">⚠ Falta tu documento</span> — Creamos tu
        cuenta, pero no pudimos subir el documento de respaldo. Inicia sesión
        y súbelo desde tu perfil para completar la verificación.
      </div>

      <LoginForm
        v-model:email="email"
        v-model:password="password"
        :is-loading="isLoading"
        :error="error"
        :is-form-valid="isFormValid"
        @submit="onSubmit"
        @donor-access="onDonorAccess"
        @org-access="onOrgAccess"
      />
    </div>
  </main>
</template>
