<script setup lang="ts">
/**
 * VIEW — Modal de alta de un insumo del catálogo. Puramente visual: recibe estado
 * por props y comunica intenciones por eventos (`close`, `submit`). El estado del
 * formulario es local a la vista.
 *
 * Excepción al "no importar del service": solo trae las CONSTANTES estáticas de
 * dominio (`CATEGORIAS_INSUMO`, `UNIDADES_INSUMO`) y el tipo del payload, no la
 * capa de datos (no llama a ninguna función del service).
 */
import { computed, ref, watch } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import {
  CATEGORIAS_INSUMO,
  UNIDADES_INSUMO,
  type CreateInsumoInput
} from '~/services/adminCatalogService'

const props = defineProps<{
  isOpen: boolean
  submitError: string | null
  isSubmitting: boolean
}>()

const emit = defineEmits<{
  close: []
  submit: [data: CreateInsumoInput]
}>()

const nombre = ref<string>('')
const categoria = ref<string>('')
const unidad = ref<string>('')

/** `true` cuando los tres campos requeridos están completos. */
const isValid = computed<boolean>(
  () => nombre.value.trim() !== '' && categoria.value !== '' && unidad.value !== ''
)

/** Limpia el formulario cada vez que el modal pasa a estar abierto. */
watch(
  () => props.isOpen,
  (open) => {
    if (!open) return
    nombre.value = ''
    categoria.value = ''
    unidad.value = ''
  }
)

/** Emite el alta solo si el formulario es válido y no está enviando. */
function onSubmit(): void {
  if (!isValid.value || props.isSubmitting) return
  emit('submit', {
    nombre: nombre.value.trim(),
    categoria: categoria.value,
    unidad: unidad.value
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
          Agregar insumo
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
            for="admin-insumo-nombre"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Nombre del insumo
          </label>
          <input
            id="admin-insumo-nombre"
            v-model="nombre"
            type="text"
            required
            placeholder="Ej: Pijama, Linterna, Kit de primeros auxilios"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Categoría -->
        <div>
          <label
            for="admin-insumo-categoria"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Categoría
          </label>
          <select
            id="admin-insumo-categoria"
            v-model="categoria"
            required
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
            <option value="" disabled>Selecciona una categoría</option>
            <option v-for="cat in CATEGORIAS_INSUMO" :key="cat.value" :value="cat.value">
              {{ cat.label }}
            </option>
          </select>
        </div>

        <!-- Unidad -->
        <div>
          <label
            for="admin-insumo-unidad"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Unidad de medida
          </label>
          <select
            id="admin-insumo-unidad"
            v-model="unidad"
            required
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
            <option value="" disabled>Selecciona una unidad</option>
            <option v-for="u in UNIDADES_INSUMO" :key="u" :value="u">
              {{ u }}
            </option>
          </select>
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
            {{ isSubmitting ? 'Agregando…' : 'Agregar al catálogo' }}
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
