<script setup lang="ts">
/**
 * VIEW — Modal de registro de una salida de stock (lote). Puramente visual:
 * recibe `isOpen`, `stock`, `availableActions` y `submitError` por props y
 * comunica intenciones por eventos (`close`, `submit`). No conoce servicios ni
 * composables; el estado del formulario es local a la vista.
 *
 * `availableActions` ya viene filtrado por el tipo de centro (la página lo deriva
 * con `accionesDisponibles(orgTipo)` del composable), por eso aquí no se importa
 * lógica de dominio: solo se renderizan las opciones recibidas.
 */
import { computed, ref, watch } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import type {
  CreateLotInput,
  LotSalida,
  StockItem
} from '~/services/distributionService'

const props = defineProps<{
  isOpen: boolean
  stock: StockItem[]
  availableActions: LotSalida[]
  submitError: string | null
}>()

const emit = defineEmits<{
  close: []
  submit: [data: CreateLotInput]
}>()

const insumoId = ref<string>('')
const cantidad = ref<number | null>(null)
const tipo = ref<LotSalida | ''>('')
const destino = ref<string>('')

/** Etiquetas del select de tipo de salida (más explícitas que el badge). */
const TIPO_OPTION_LABEL: Record<LotSalida, string> = {
  enviado_a_terreno: 'Enviar a terreno (otro punto)',
  entregado_a_beneficiario: 'Entregar a personas'
}

/** Insumo de stock actualmente seleccionado (fuente del tope de cantidad). */
const selectedStock = computed<StockItem | undefined>(() =>
  props.stock.find((s) => s.insumoId === insumoId.value)
)

/** Máximo que se puede registrar: lo disponible del insumo elegido. */
const maxCantidad = computed<number>(() => selectedStock.value?.cantidadDisponible ?? 0)

/** Placeholder del destino según el tipo de salida elegido. */
const destinoPlaceholder = computed<string>(() => {
  if (tipo.value === 'enviado_a_terreno') return 'Ej: Centro Los Ángeles'
  if (tipo.value === 'entregado_a_beneficiario') return 'Ej: Sector norte, familias'
  return 'Destino de la entrega'
})

/** Mensaje de error de la cantidad en tiempo real (o null si es válida). */
const cantidadError = computed<string | null>(() => {
  if (cantidad.value === null) return null
  if (cantidad.value <= 0) return 'La cantidad debe ser mayor a 0'
  if (cantidad.value > maxCantidad.value) {
    return `Solo hay ${maxCantidad.value} disponibles`
  }
  return null
})

/** El formulario es válido si todos los campos cumplen sus reglas. */
const isValid = computed<boolean>(
  () =>
    !!selectedStock.value &&
    cantidad.value !== null &&
    cantidad.value > 0 &&
    cantidad.value <= maxCantidad.value &&
    !!tipo.value &&
    destino.value.trim().length > 0
)

/** Resetea el formulario cada vez que el modal pasa a estar abierto. */
watch(
  () => props.isOpen,
  (open) => {
    if (!open) return
    insumoId.value = ''
    cantidad.value = null
    destino.value = ''
    // Si solo hay una acción posible, se preselecciona; si hay dos, se elige.
    tipo.value = props.availableActions.length === 1 ? props.availableActions[0]! : ''
  }
)

/** Emite el lote solo si la validación pasa, resolviendo los datos del insumo. */
function onSubmit(): void {
  if (!isValid.value || !selectedStock.value || !tipo.value || cantidad.value === null) {
    return
  }
  emit('submit', {
    insumoId: selectedStock.value.insumoId,
    cantidad: cantidad.value,
    tipo: tipo.value,
    destino: destino.value.trim()
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
          Registrar distribución
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
        <!-- Insumo (desde stock) -->
        <div>
          <label
            for="lot-insumo"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Insumo
          </label>
          <select
            id="lot-insumo"
            v-model="insumoId"
            required
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
            <option value="" disabled>Selecciona un insumo</option>
            <option v-for="item in stock" :key="item.insumoId" :value="item.insumoId">
              {{ item.insumoNombre }} — {{ item.cantidadDisponible }} {{ item.unidad }} disp.
            </option>
          </select>
        </div>

        <!-- Cantidad -->
        <div>
          <label
            for="lot-cantidad"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Cantidad
          </label>
          <input
            id="lot-cantidad"
            v-model.number="cantidad"
            type="number"
            min="1"
            :max="maxCantidad || undefined"
            :disabled="!selectedStock"
            required
            placeholder="0"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600
                   disabled:cursor-not-allowed disabled:bg-slate-100"
          >
          <p v-if="cantidadError" class="mt-1 text-xs text-alert">
            {{ cantidadError }}
          </p>
          <p v-else-if="selectedStock" class="mt-1 text-xs text-slate-400">
            Máximo {{ maxCantidad }} {{ selectedStock.unidad }}
          </p>
        </div>

        <!-- Tipo de salida (filtrado por el tipo de centro) -->
        <div>
          <label
            for="lot-tipo"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Tipo de salida
          </label>
          <select
            id="lot-tipo"
            v-model="tipo"
            required
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
            <option value="" disabled>Selecciona el tipo</option>
            <option v-for="accion in availableActions" :key="accion" :value="accion">
              {{ TIPO_OPTION_LABEL[accion] }}
            </option>
          </select>
        </div>

        <!-- Destino -->
        <div>
          <label
            for="lot-destino"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Destino
          </label>
          <input
            id="lot-destino"
            v-model="destino"
            type="text"
            required
            :placeholder="destinoPlaceholder"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Error de envío (p. ej. stock insuficiente) -->
        <p v-if="submitError" class="text-sm text-alert">
          {{ submitError }}
        </p>

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
            :disabled="!isValid"
          >
            Registrar salida
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>
