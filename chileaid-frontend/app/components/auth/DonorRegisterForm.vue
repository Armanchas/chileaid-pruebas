<script setup lang="ts">
import BaseButton from '~/components/ui/BaseButton.vue'

/**
 * VIEW — Formulario de registro de donante con estética glassmorphic.
 * Puramente visual: recibe su estado por props (valores vía v-model, validez y
 * errores ya calculados por el ViewModel) y comunica intenciones por eventos.
 * No conoce servicios ni composables; toda la lógica de validación vive arriba.
 */
const props = defineProps<{
  nombre: string
  apellido: string
  email: string
  password: string
  confirmPassword: string
  isLoading: boolean
  error: string | null
  isFormValid: boolean
  nombreError: string | null
  apellidoError: string | null
  emailError: string | null
  passwordError: string | null
  confirmPasswordError: string | null
}>()

const emit = defineEmits<{
  'update:nombre': [value: string]
  'update:apellido': [value: string]
  'update:email': [value: string]
  'update:password': [value: string]
  'update:confirmPassword': [value: string]
  submit: [data: { nombre: string; apellido: string; email: string; password: string; confirmPassword: string }]
  'go-to-login': []
  'field-touched': [payload: { field: string }]
}>()

function onSubmit(): void {
  if (!props.isFormValid || props.isLoading) return
  emit('submit', {
    nombre: props.nombre,
    apellido: props.apellido,
    email: props.email,
    password: props.password,
    confirmPassword: props.confirmPassword
  })
}
</script>

<template>
  <div class="glass-auth w-full max-w-md rounded-2xl p-7 sm:p-9">
    <header class="border-b border-navy-800/10 pb-5">
      <h1 class="font-display text-3xl font-black uppercase text-navy-800 sm:text-4xl">
        Crear cuenta
      </h1>
      <p class="mt-2 text-navy-600">
        Regístrate como donante para coordinar y seguir tu ayuda.
      </p>
    </header>

    <form class="mt-6 space-y-5" novalidate @submit.prevent="onSubmit">
      <!-- Nombre y apellido: dos columnas en desktop, una en mobile -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <!-- Nombre -->
        <div>
          <label
            for="register-nombre"
            class="font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Nombre
          </label>
          <input
            id="register-nombre"
            :value="nombre"
            type="text"
            autocomplete="given-name"
            placeholder="Tu nombre"
            :aria-invalid="!!nombreError"
            class="mt-2 w-full rounded-lg border bg-white/70 px-4 py-3 text-navy-900
                   placeholder-slate-400 transition-colors duration-200
                   focus:bg-white focus:outline-none focus-visible:ring-4 focus-visible:ring-navy-600/20"
            :class="nombreError
              ? 'border-alert-500/70 focus:border-alert-500'
              : 'border-navy-800/15 focus:border-navy-600/50'"
            @input="emit('update:nombre', ($event.target as HTMLInputElement).value)"
            @blur="emit('field-touched', { field: 'nombre' })"
          >
          <p v-if="nombreError" class="mt-1.5 text-sm font-semibold text-alert-500">
            {{ nombreError }}
          </p>
        </div>

        <!-- Apellido -->
        <div>
          <label
            for="register-apellido"
            class="font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Apellido
          </label>
          <input
            id="register-apellido"
            :value="apellido"
            type="text"
            autocomplete="family-name"
            placeholder="Tu apellido"
            :aria-invalid="!!apellidoError"
            class="mt-2 w-full rounded-lg border bg-white/70 px-4 py-3 text-navy-900
                   placeholder-slate-400 transition-colors duration-200
                   focus:bg-white focus:outline-none focus-visible:ring-4 focus-visible:ring-navy-600/20"
            :class="apellidoError
              ? 'border-alert-500/70 focus:border-alert-500'
              : 'border-navy-800/15 focus:border-navy-600/50'"
            @input="emit('update:apellido', ($event.target as HTMLInputElement).value)"
            @blur="emit('field-touched', { field: 'apellido' })"
          >
          <p v-if="apellidoError" class="mt-1.5 text-sm font-semibold text-alert-500">
            {{ apellidoError }}
          </p>
        </div>
      </div>

      <!-- Email -->
      <div>
        <label
          for="register-email"
          class="font-display text-sm font-bold uppercase tracking-widest text-navy-600"
        >
          Correo electrónico
        </label>
        <input
          id="register-email"
          :value="email"
          type="email"
          autocomplete="email"
          inputmode="email"
          placeholder="tu@correo.cl"
          :aria-invalid="!!emailError"
          class="mt-2 w-full rounded-lg border bg-white/70 px-4 py-3 text-navy-900
                 placeholder-slate-400 transition-colors duration-200
                 focus:bg-white focus:outline-none focus-visible:ring-4 focus-visible:ring-navy-600/20"
          :class="emailError
            ? 'border-alert-500/70 focus:border-alert-500'
            : 'border-navy-800/15 focus:border-navy-600/50'"
          @input="emit('update:email', ($event.target as HTMLInputElement).value)"
          @blur="emit('field-touched', { field: 'email' })"
        >
        <p v-if="emailError" class="mt-1.5 text-sm font-semibold text-alert-500">
          {{ emailError }}
        </p>
      </div>

      <!-- Password -->
      <div>
        <label
          for="register-password"
          class="font-display text-sm font-bold uppercase tracking-widest text-navy-600"
        >
          Contraseña
        </label>
        <input
          id="register-password"
          :value="password"
          type="password"
          autocomplete="new-password"
          placeholder="Mínimo 6 caracteres"
          :aria-invalid="!!passwordError"
          class="mt-2 w-full rounded-lg border bg-white/70 px-4 py-3 text-navy-900
                 placeholder-slate-400 transition-colors duration-200
                 focus:bg-white focus:outline-none focus-visible:ring-4 focus-visible:ring-navy-600/20"
          :class="passwordError
            ? 'border-alert-500/70 focus:border-alert-500'
            : 'border-navy-800/15 focus:border-navy-600/50'"
          @input="emit('update:password', ($event.target as HTMLInputElement).value)"
          @blur="emit('field-touched', { field: 'password' })"
        >
        <p v-if="passwordError" class="mt-1.5 text-sm font-semibold text-alert-500">
          {{ passwordError }}
        </p>
      </div>

      <!-- Confirmar contraseña -->
      <div>
        <label
          for="register-confirm-password"
          class="font-display text-sm font-bold uppercase tracking-widest text-navy-600"
        >
          Confirmar contraseña
        </label>
        <input
          id="register-confirm-password"
          :value="confirmPassword"
          type="password"
          autocomplete="new-password"
          placeholder="Repite tu contraseña"
          :aria-invalid="!!confirmPasswordError"
          class="mt-2 w-full rounded-lg border bg-white/70 px-4 py-3 text-navy-900
                 placeholder-slate-400 transition-colors duration-200
                 focus:bg-white focus:outline-none focus-visible:ring-4 focus-visible:ring-navy-600/20"
          :class="confirmPasswordError
            ? 'border-alert-500/70 focus:border-alert-500'
            : 'border-navy-800/15 focus:border-navy-600/50'"
          @input="emit('update:confirmPassword', ($event.target as HTMLInputElement).value)"
          @blur="emit('field-touched', { field: 'confirmPassword' })"
        >
        <p v-if="confirmPasswordError" class="mt-1.5 text-sm font-semibold text-alert-500">
          {{ confirmPasswordError }}
        </p>
      </div>

      <!-- Mensaje de error global -->
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
        {{ isLoading ? 'Creando cuenta…' : 'Crear cuenta' }}
      </BaseButton>
    </form>

    <!-- Separador -->
    <div class="my-7 flex items-center gap-4">
      <span class="h-px flex-1 bg-navy-800/15" />
      <span class="font-display text-xs font-bold uppercase tracking-widest text-navy-600">
        ¿Ya tienes cuenta?
      </span>
      <span class="h-px flex-1 bg-navy-800/15" />
    </div>

    <!-- Acceso a inicio de sesión -->
    <BaseButton
      variant="ghost"
      full-width
      class="border border-navy-600/25"
      @click="emit('go-to-login')"
    >
      Ingresar
    </BaseButton>
  </div>
</template>
