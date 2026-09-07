<script setup lang="ts">
import BaseButton from '~/components/ui/BaseButton.vue'

/**
 * VIEW — Formulario de acceso con estética glassmorphic. Puramente visual:
 * recibe su estado por props y comunica intenciones por eventos. No conoce
 * servicios ni composables; la validación de negocio vive en el ViewModel
 * (la prop `isFormValid`).
 */
const props = defineProps<{
  email: string
  password: string
  isLoading: boolean
  error: string | null
  isFormValid: boolean
}>()

const emit = defineEmits<{
  'update:email': [value: string]
  'update:password': [value: string]
  submit: [credentials: { email: string; password: string }]
  donorAccess: []
  orgAccess: []
}>()

function onSubmit(): void {
  if (!props.isFormValid || props.isLoading) return
  emit('submit', { email: props.email, password: props.password })
}
</script>

<template>
  <div class="glass-auth w-full max-w-md rounded-2xl p-7 sm:p-9">
    <header class="border-b border-navy-800/10 pb-5">
      <h1 class="font-display text-3xl font-black uppercase text-navy-800 sm:text-4xl">
        Iniciar sesión
      </h1>
      <p class="mt-2 text-navy-600">
        Accede para coordinar y dar seguimiento a la ayuda.
      </p>
    </header>

    <form class="mt-6 space-y-5" novalidate @submit.prevent="onSubmit">
      <!-- Email -->
      <div>
        <label
          for="login-email"
          class="font-display text-sm font-bold uppercase tracking-widest text-navy-600"
        >
          Correo electrónico
        </label>
        <input
          id="login-email"
          :value="email"
          type="email"
          autocomplete="email"
          inputmode="email"
          placeholder="tu@correo.cl"
          class="mt-2 w-full rounded-lg border border-navy-800/15 bg-white/70 px-4 py-3 text-navy-900
                 placeholder-slate-400 transition-colors duration-200
                 focus:border-navy-600/50 focus:bg-white focus:outline-none
                 focus-visible:ring-4 focus-visible:ring-navy-600/20"
          @input="emit('update:email', ($event.target as HTMLInputElement).value)"
        >
      </div>

      <!-- Password -->
      <div>
        <label
          for="login-password"
          class="font-display text-sm font-bold uppercase tracking-widest text-navy-600"
        >
          Contraseña
        </label>
        <input
          id="login-password"
          :value="password"
          type="password"
          autocomplete="current-password"
          placeholder="Mínimo 6 caracteres"
          class="mt-2 w-full rounded-lg border border-navy-800/15 bg-white/70 px-4 py-3 text-navy-900
                 placeholder-slate-400 transition-colors duration-200
                 focus:border-navy-600/50 focus:bg-white focus:outline-none
                 focus-visible:ring-4 focus-visible:ring-navy-600/20"
          @input="emit('update:password', ($event.target as HTMLInputElement).value)"
        >
      </div>

      <!-- Mensaje de error -->
      <p
        v-if="error"
        role="alert"
        class="rounded-lg bg-alert/20 px-4 py-3 text-sm font-semibold text-alert-500 ring-1 ring-alert/40"
      >
        {{ error }}
      </p>

      <BaseButton
        type="submit"
        variant="navy"
        size="lg"
        full-width
        :disabled="!isFormValid || isLoading"
      >
        {{ isLoading ? 'Verificando…' : 'Entrar' }}
      </BaseButton>
    </form>

    <!-- Separador -->
    <div class="my-7 flex items-center gap-4">
      <span class="h-px flex-1 bg-navy-800/15" />
      <span class="font-display text-xs font-bold uppercase tracking-widest text-navy-600">
        ¿No tienes cuenta?
      </span>
      <span class="h-px flex-1 bg-navy-800/15" />
    </div>

    <!-- Accesos secundarios -->
    <div class="flex flex-col gap-3 sm:flex-row">
      <BaseButton
        variant="ghost"
        full-width
        class="border border-navy-600/25"
        @click="emit('donorAccess')"
      >
        Soy Donante
      </BaseButton>
      <BaseButton
        variant="ghost"
        full-width
        class="border border-navy-600/25"
        @click="emit('orgAccess')"
      >
        Soy Organización
      </BaseButton>
    </div>
  </div>
</template>
