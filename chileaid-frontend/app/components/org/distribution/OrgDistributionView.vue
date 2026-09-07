<script setup lang="ts">
/**
 * VIEW — Distribución de inventario de la organización receptora. Puramente
 * visual: recibe todo por props y comunica intenciones por eventos. No conoce
 * servicios ni composables; el mapeo tipo→badge es lógica de presentación.
 *
 * Dos secciones: stock disponible (cards por insumo) e historial de lotes ya
 * distribuidos. La acción de registrar una salida vive en el modal (lo monta la
 * página); aquí solo se emite `open-create`.
 */
import BaseButton from '~/components/ui/BaseButton.vue'
import type { DistributionLotDTO, LotSalida, StockItem } from '~/services/distributionService'

defineProps<{
  lots: DistributionLotDTO[]
  stock: StockItem[]
  isLoading: boolean
  totalDistribuido: number
}>()

const emit = defineEmits<{
  'open-create': []
}>()

/** Clases del badge según el tipo de salida del lote. */
const TIPO_BADGE: Record<LotSalida, string> = {
  enviado_a_terreno: 'bg-orange-100 text-orange-700',
  entregado_a_beneficiario: 'bg-teal-100 text-teal-800'
}

/** Etiqueta corta del badge (la versión larga vive en el modal). */
const TIPO_LABEL: Record<LotSalida, string> = {
  enviado_a_terreno: 'Enviado a terreno',
  entregado_a_beneficiario: 'Entregado'
}

/** Capitaliza el value del enum de categoría (backend lo envía en minúscula). */
function categoriaLabel(categoria: string): string {
  return categoria.charAt(0).toUpperCase() + categoria.slice(1)
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
    <!-- ===== HEADER ===== -->
    <header class="flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0">
        <h1 class="font-display text-2xl font-black uppercase text-navy-800">
          Distribución de inventario
        </h1>
        <p class="mt-1 text-slate-500">
          {{ totalDistribuido }} {{ totalDistribuido === 1 ? 'unidad distribuida' : 'unidades distribuidas' }}
        </p>
      </div>
      <BaseButton variant="navy" size="md" @click="emit('open-create')">
        <svg
          class="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M12 5v14" />
          <path d="M5 12h14" />
        </svg>
        Registrar distribución
      </BaseButton>
    </header>

    <!-- ===== SECCIÓN: STOCK DISPONIBLE ===== -->
    <section class="mt-8">
      <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
        Stock disponible
      </h2>

      <!-- Loading skeleton -->
      <div
        v-if="isLoading && stock.length === 0"
        class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        <div v-for="n in 4" :key="n" class="h-32 animate-pulse rounded-2xl bg-slate-200" />
      </div>

      <!-- Vacío -->
      <p v-else-if="stock.length === 0" class="mt-4 text-sm text-slate-400">
        No hay stock disponible para distribuir.
      </p>

      <!-- Grid de cards -->
      <!-- Sin barra de progreso: StockItem no expone el total recibido, solo el
           disponible; sin la meta no se puede calcular un % honesto. -->
      <ul v-else class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <li
          v-for="item in stock"
          :key="item.insumoId"
          class="glass-auth flex flex-col rounded-2xl p-5"
        >
          <h3 class="font-display text-base font-black uppercase leading-tight text-navy-800">
            {{ item.insumoNombre }}
          </h3>
          <p class="mt-0.5 text-xs text-slate-400">
            {{ categoriaLabel(item.categoria) }}
          </p>
          <p class="mt-4 font-display text-4xl font-black leading-none text-navy-800">
            {{ item.cantidadDisponible }}
          </p>
          <p class="mt-1 text-xs uppercase tracking-wide text-slate-500">
            {{ item.unidad }} disponibles
          </p>
        </li>
      </ul>
    </section>

    <!-- ===== SECCIÓN: HISTORIAL DE LOTES ===== -->
    <section class="mt-8">
      <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
        Historial de lotes
      </h2>

      <!-- Loading skeleton -->
      <div v-if="isLoading && lots.length === 0" class="mt-4 flex flex-col gap-3">
        <div v-for="n in 3" :key="n" class="h-16 animate-pulse rounded-xl bg-slate-200" />
      </div>

      <!-- Vacío -->
      <div
        v-else-if="lots.length === 0"
        class="glass-auth mt-4 rounded-2xl px-4 py-12 text-center"
      >
        <p class="text-sm text-slate-500">
          Aún no has registrado ninguna distribución.
        </p>
      </div>

      <!-- Lista de lotes -->
      <ul v-else class="mt-4 flex flex-col gap-3">
        <li
          v-for="lot in lots"
          :key="lot.id"
          class="glass-auth flex flex-wrap items-center justify-between gap-3 rounded-xl px-4 py-3"
        >
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <span
                class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                :class="TIPO_BADGE[lot.tipo]"
              >
                {{ TIPO_LABEL[lot.tipo] }}
              </span>
              <span class="text-sm font-semibold text-navy-800">
                {{ lot.insumoNombre }}
              </span>
              <span class="text-sm text-slate-500">
                {{ lot.cantidad }} {{ lot.unidad }}
              </span>
            </div>
            <p class="mt-1 text-xs text-slate-500">
              Destino: <span class="text-navy-800">{{ lot.destino }}</span>
            </p>
          </div>
          <span class="shrink-0 text-xs text-slate-400">
            {{ lot.fecha }}
          </span>
        </li>
      </ul>
    </section>
  </div>
</template>
