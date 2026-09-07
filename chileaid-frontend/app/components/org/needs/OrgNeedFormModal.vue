<script setup lang="ts">
/**
 * VIEW — Modal de alta/edición de una necesidad. Puramente visual: recibe
 * `isOpen`, `catalog` e `initialData` por props y comunica intenciones por
 * eventos (`close`, `submit`). No conoce servicios ni composables; el estado del
 * formulario es local a la vista.
 *
 * Dos modos:
 *  - Alta (sin `initialData`): se elige el insumo del catálogo en el `<select>`.
 *  - Edición (con `initialData`): el insumo queda PRESELECCIONADO y BLOQUEADO; el
 *    insumo no se puede cambiar, solo `cantidadRequerida` y `urgencia`. El botón
 *    principal cambia a "Guardar cambios".
 *
 * El guardado (POST/PUT) lo ejecuta el VM; aquí solo se reflejan su estado
 * (`isSubmitting` deshabilita los botones) y su error (`submitError`, típicamente
 * el `detail` del backend) sin cerrar el modal.
 */
import { computed, ref, watch } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import type { CreateNeedInput, InsumoCatalogDTO } from '~/services/orgNeedsService'
import type { NeedDTO, Urgencia } from '~/services/orgDashboardService'

const props = defineProps<{
  isOpen: boolean
  catalog: InsumoCatalogDTO[]
  initialData?: NeedDTO | null
  isSubmitting?: boolean
  submitError?: string | null
}>()

const emit = defineEmits<{
  close: []
  submit: [data: CreateNeedInput]
}>()

const insumoId = ref<string>('')
const cantidadRequerida = ref<number>(1)
const urgencia = ref<Urgencia>('media')

/** `true` cuando el modal abre sobre una necesidad existente. */
const isEditing = computed<boolean>(() => !!props.initialData)

/**
 * Sincroniza el formulario cada vez que el modal pasa a estar abierto: precarga
 * cantidad y urgencia desde `initialData` en edición (el insumo no se edita: se
 * muestra solo lectura), o deja los campos en blanco en alta.
 */
watch(
  () => props.isOpen,
  (open) => {
    if (!open) return
    insumoId.value = '' // en edición el insumo no se elige (se muestra read-only)
    cantidadRequerida.value = props.initialData?.cantidadRequerida ?? 1
    urgencia.value = props.initialData?.urgencia ?? 'media'
  }
)

/**
 * Emite el alta/edición. En alta exige un insumo elegido; en edición el insumo no
 * aplica (lo editable es cantidad + urgencia). Siempre exige cantidad >= 1.
 */
function onSubmit(): void {
  if (props.isSubmitting) return
  if (cantidadRequerida.value < 1) return
  if (!isEditing.value && !insumoId.value) return
  emit('submit', {
    insumoId: insumoId.value,
    cantidadRequerida: cantidadRequerida.value,
    urgencia: urgencia.value
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
          {{ isEditing ? 'Editar necesidad' : 'Nueva necesidad' }}
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
        <!-- Insumo (catálogo) — en edición se muestra solo lectura -->
        <div>
          <label
            for="need-insumo"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Insumo
          </label>

          <!-- Edición: el insumo no se cambia, se muestra el de la necesidad -->
          <template v-if="isEditing">
            <p class="mt-1 w-full rounded-lg bg-slate-100 px-3 py-2.5 text-sm text-slate-500">
              {{ initialData?.insumo.nombre }} ({{ initialData?.insumo.categoria }})
            </p>
            <p class="mt-1 text-xs text-slate-400">
              El insumo no se puede cambiar al editar.
            </p>
          </template>

          <!-- Alta: se elige del catálogo -->
          <select
            v-else
            id="need-insumo"
            v-model="insumoId"
            required
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
            <option value="" disabled>Selecciona un insumo</option>
            <option v-for="insumo in catalog" :key="insumo.id" :value="insumo.id">
              {{ insumo.nombre }} ({{ insumo.categoria }})
            </option>
          </select>
        </div>

        <!-- Cantidad requerida -->
        <div>
          <label
            for="need-cantidad"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Cantidad requerida
          </label>
          <input
            id="need-cantidad"
            v-model.number="cantidadRequerida"
            type="number"
            min="1"
            required
            placeholder="Ej: 200"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Urgencia -->
        <div>
          <label
            for="need-urgencia"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Urgencia
          </label>
          <select
            id="need-urgencia"
            v-model="urgencia"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
            <option value="alta">Alta (urgente)</option>
            <option value="media">Media</option>
            <option value="baja">Baja</option>
          </select>
        </div>

        <!-- Error del backend (no cierra el modal) -->
        <p
          v-if="submitError"
          class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
          role="alert"
        >
          {{ submitError }}
        </p>

        <!-- Acciones -->
        <div class="mt-2 flex gap-3">
          <BaseButton
            variant="ghost"
            size="md"
            :full-width="true"
            :disabled="isSubmitting"
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
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Guardando…' : isEditing ? 'Guardar cambios' : 'Crear necesidad' }}
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>
