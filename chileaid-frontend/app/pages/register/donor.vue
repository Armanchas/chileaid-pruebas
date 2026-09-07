<script setup lang="ts">
/**
 * PÁGINA — Solo orquesta. Toma el ViewModel de registro de donante y reparte
 * su estado y acciones al formulario vía props/eventos. Sin lógica de negocio
 * ni datos.
 */
import { useDonorRegisterViewModel } from '~/composables/useDonorRegisterViewModel'
import DonorRegisterForm from '~/components/auth/DonorRegisterForm.vue'

const {
  nombre,
  apellido,
  email,
  password,
  confirmPassword,
  isLoading,
  error,
  isFormValid,
  nombreError,
  apellidoError,
  emailError,
  passwordError,
  confirmPasswordError,
  onFieldTouched,
  onSubmit,
  onGoToLogin
} = useDonorRegisterViewModel()
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
        class="alert-pulse mb-4 inline-flex items-center gap-2 rounded-full bg-alert px-4 py-1.5
               font-display text-sm font-bold uppercase tracking-widest text-white"
      >
        <span class="h-2 w-2 rounded-full bg-white" />
        Chile Aid
      </NuxtLink>

      <!-- Subtítulo bajo el badge -->
      <p class="mb-8 text-center font-display text-base uppercase tracking-widest text-navy-600">
        Únete a la red de ayuda humanitaria
      </p>

      <DonorRegisterForm
        v-model:nombre="nombre"
        v-model:apellido="apellido"
        v-model:email="email"
        v-model:password="password"
        v-model:confirm-password="confirmPassword"
        :is-loading="isLoading"
        :error="error"
        :is-form-valid="isFormValid"
        :nombre-error="nombreError"
        :apellido-error="apellidoError"
        :email-error="emailError"
        :password-error="passwordError"
        :confirm-password-error="confirmPasswordError"
        @submit="onSubmit"
        @go-to-login="onGoToLogin"
        @field-touched="(payload) => onFieldTouched(payload.field as 'nombre' | 'apellido' | 'email' | 'password' | 'confirmPassword')"
      />
    </div>
  </main>
</template>
