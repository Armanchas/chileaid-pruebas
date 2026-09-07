<script setup lang="ts">
/**
 * VIEW — Modal de alta de una emergencia. Puramente visual: recibe estado por
 * props y comunica intenciones por eventos (`close`, `submit`). El estado del
 * formulario es local a la vista.
 *
 * Excepción al "no importar del service": solo trae la CONSTANTE estática de
 * dominio (`TIPOS_EMERGENCIA`) y el tipo del payload, no la capa de datos.
 */
import { computed, ref, watch } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import {
  TIPOS_EMERGENCIA,
  type CreateEmergencyInput,
  type EmergencyType
} from '~/services/adminEmergenciesService'

const props = defineProps<{
  isOpen: boolean
  submitError: string | null
  isSubmitting: boolean
}>()

const emit = defineEmits<{
  close: []
  submit: [data: CreateEmergencyInput]
}>()

const nombre = ref<string>('')
const tipo = ref<EmergencyType | ''>('')
const zona = ref<string>('')
const fechaInicio = ref<string>('')

/** `true` cuando los cuatro campos requeridos están completos. */
const isValid = computed<boolean>(
  () =>
    nombre.value.trim() !== '' &&
    tipo.value !== '' &&
    zona.value.trim() !== '' &&
    fechaInicio.value !== ''
)

/** Limpia el formulario cada vez que el modal pasa a estar abierto. */
watch(
  () => props.isOpen,
  (open) => {
    if (!open) return
    nombre.value = ''
    tipo.value = ''
    zona.value = ''
    fechaInicio.value = ''
  }
)

/** Emite el alta solo si el formulario es válido y no está enviando. */
function onSubmit(): void {
  if (!isValid.value || props.isSubmitting || tipo.value === '') return
  emit('submit', {
    nombre: nombre.value.trim(),
    tipo: tipo.value,
    zona: zona.value.trim(),
    fechaInicio: fechaInicio.value
  })
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
    @click.self="emit('close')"
  >
    <div class="glass-auth w-full max-w-md rounded-2xl p-6">
      <!-- Header -->
      <div class="flex items-center justify-between gap-3">
        <h2 class="font-display text-lg font-black uppercase text-navy-800">
          Nueva emergencia
        </h2>
        <button
          type="button"
          class="flex h-8 w-8 items-center justify-center rounded-full text-slate-400
                 transition-colors hover:bg-navy-800/8 hover:text-navy-800"
          aria-label="Cerrar"
          @click="emit('close')"
        >
          <svg
            class="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Formulario -->
      <form class="mt-5 flex flex-col gap-4" @submit.prevent="onSubmit">
        <!-- Nombre -->
        <div>
          <label
            for="admin-emergency-nombre"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Nombre de la emergencia
          </label>
          <input
            id="admin-emergency-nombre"
            v-model="nombre"
            type="text"
            required
            placeholder="Ej: Incendio Forestal Victoria 2026"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
          <p class="mt-1 text-xs text-slate-500">
            Usa un nombre específico: dos eventos del mismo tipo y región deben ser
            distinguibles.
          </p>
        </div>

        <!-- Tipo -->
        <div>
          <label
            for="admin-emergency-tipo"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Tipo
          </label>
          <select
            id="admin-emergency-tipo"
            v-model="tipo"
            required
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
            <option value="" disabled>Selecciona un tipo</option>
            <option v-for="t in TIPOS_EMERGENCIA" :key="t.value" :value="t.value">
              {{ t.label }}
            </option>
          </select>
        </div>

        <!-- Zona -->
        <div>
          <label
            for="admin-emergency-zona"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Zona
          </label>
          <input
            id="admin-emergency-zona"
            v-model="zona"
            type="text"
            required
            placeholder="Ej: La Araucanía"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Fecha de inicio -->
        <div>
          <label
            for="admin-emergency-fecha"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Fecha de inicio
          </label>
          <input
            id="admin-emergency-fecha"
            v-model="fechaInicio"
            type="date"
            required
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Acciones -->
        <div class="mt-2 flex gap-3">
          <BaseButton
            variant="ghost"
            size="md"
            :full-width="true"
            class="border border-navy-600/25"
            @click="emit('close')"
          >
            Cancelar
          </BaseButton>
          <BaseButton
            type="submit"
            variant="navy"
            size="md"
            :full-width="true"
            :disabled="!isValid || isSubmitting"
          >
            {{ isSubmitting ? 'Creando…' : 'Crear emergencia' }}
          </BaseButton>
        </div>

        <!-- Error de envío -->
        <p v-if="submitError" class="text-sm text-alert">
          {{ submitError }}
        </p>
      </form>
    </div>
  </div>
</template>
