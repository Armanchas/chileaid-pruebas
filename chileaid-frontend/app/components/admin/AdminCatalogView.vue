<script setup lang="ts">
/**
 * VIEW — Gestión del catálogo de insumos del administrador. Puramente visual:
 * recibe todo por props y comunica intenciones por eventos. No conoce servicios
 * ni composables; el color del badge por categoría y la confirmación de borrado
 * son lógica de presentación.
 */
import { computed } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import type { InsumoCatalogDTO } from '~/services/adminCatalogService'

const props = defineProps<{
  catalog: InsumoCatalogDTO[]
  isLoading: boolean
  error: string | null
  deletingId: string | null
  searchQuery: string
  selectedCategoria: string
  categoriasCounts: Record<string, number>
}>()

const emit = defineEmits<{
  'open-create': []
  'delete-insumo': [id: string]
  'update:search': [q: string]
  'set-categoria': [c: string]
}>()

/** Categorías con conteo (sin la entrada agregada `todas`), para las pills. */
const categoriaPills = computed<string[]>(() =>
  Object.keys(props.categoriasCounts).filter((k) => k !== 'todas')
)

/**
 * Color del badge por categoría (colores Tailwind por defecto). Las keys son los
 * values del enum `InsumoCategory` del backend (lo que viaja en `categoria`).
 */
const CATEGORIA_COLOR: Record<string, string> = {
  agua: 'bg-sky-100 text-sky-700',
  alimentos: 'bg-green-100 text-green-700',
  ropa: 'bg-indigo-100 text-indigo-700',
  abrigo: 'bg-blue-100 text-blue-700',
  higiene: 'bg-cyan-100 text-cyan-700',
  medicamentos: 'bg-red-100 text-red-700',
  otros: 'bg-slate-100 text-slate-600'
}

/** Clases del badge para una categoría (con fallback neutro). */
function categoriaColor(categoria: string): string {
  return CATEGORIA_COLOR[categoria] ?? 'bg-slate-100 text-slate-600'
}

/** Etiqueta legible de una categoría (capitaliza el value del enum: agua→Agua). */
function categoriaLabel(categoria: string): string {
  return categoria.charAt(0).toUpperCase() + categoria.slice(1)
}

/** Propaga el término de búsqueda tecleado. */
function onSearchInput(event: Event): void {
  emit('update:search', (event.target as HTMLInputElement).value)
}

/** Pide confirmación antes de emitir la baja del insumo. */
function confirmDelete(insumo: InsumoCatalogDTO): void {
  const ok = window.confirm(
    `¿Eliminar '${insumo.nombre}' del catálogo? Las organizaciones no podrán solicitar este insumo.`
  )
  if (ok) emit('delete-insumo', insumo.id)
}

/** Restablece los filtros (búsqueda + categoría). */
function clearFilters(): void {
  emit('update:search', '')
  emit('set-categoria', 'todas')
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
    <!-- ===== HEADER ===== -->
    <header class="flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0">
        <h1 class="font-display text-2xl font-black uppercase text-navy-800">
          Catálogo de insumos
        </h1>
        <p class="mt-1 text-slate-500">
          Insumos disponibles para que las organizaciones publiquen solicitudes
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
        Agregar insumo
      </BaseButton>
    </header>

    <!-- ===== BARRA DE FILTROS ===== -->
    <div class="mt-6 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <!-- Búsqueda -->
      <div class="relative w-full lg:max-w-xs">
        <svg
          class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <input
          :value="searchQuery"
          type="text"
          placeholder="Buscar insumo…"
          class="w-full rounded-lg bg-white py-2.5 pl-9 pr-3 text-sm text-navy-900
                 placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                 focus:outline-none focus:ring-2 focus:ring-navy-600"
          @input="onSearchInput"
        >
      </div>

      <!-- Pills de categoría -->
      <div class="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
        <button
          type="button"
          class="shrink-0 rounded-full px-3 py-1.5 font-display text-xs font-bold uppercase
                 tracking-widest transition-colors duration-200"
          :class="selectedCategoria === 'todas'
            ? 'bg-navy-800 text-white'
            : 'bg-white text-navy-600 border border-navy-600/20 hover:bg-navy-800/5'"
          @click="emit('set-categoria', 'todas')"
        >
          Todas ({{ categoriasCounts.todas ?? 0 }})
        </button>
        <button
          v-for="cat in categoriaPills"
          :key="cat"
          type="button"
          class="shrink-0 rounded-full px-3 py-1.5 font-display text-xs font-bold uppercase
                 tracking-widest transition-colors duration-200"
          :class="selectedCategoria === cat
            ? 'bg-navy-800 text-white'
            : 'bg-white text-navy-600 border border-navy-600/20 hover:bg-navy-800/5'"
          @click="emit('set-categoria', cat)"
        >
          {{ categoriaLabel(cat) }} ({{ categoriasCounts[cat] ?? 0 }})
        </button>
      </div>
    </div>

    <!-- ===== ERROR ===== -->
    <p
      v-if="error"
      role="alert"
      class="mt-6 rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
    >
      {{ error }}
    </p>

    <!-- ===== LOADING (skeleton: 6 filas) ===== -->
    <div v-if="isLoading && catalog.length === 0" class="mt-6 flex flex-col gap-2">
      <div
        v-for="n in 6"
        :key="n"
        class="h-14 animate-pulse rounded-xl bg-slate-200"
      />
    </div>

    <!-- ===== VACÍO TRAS FILTROS ===== -->
    <div
      v-else-if="catalog.length === 0"
      class="glass-auth mt-6 rounded-2xl px-4 py-12 text-center"
    >
      <p class="text-sm text-slate-500">No se encontraron insumos con esos filtros</p>
      <BaseButton
        variant="ghost"
        size="md"
        class="mt-4 border border-navy-600/25"
        @click="clearFilters"
      >
        Limpiar filtros
      </BaseButton>
    </div>

    <!-- ===== CONTENIDO ===== -->
    <template v-else>
      <!-- Tabla (desktop) -->
      <div class="mt-6 hidden overflow-hidden rounded-2xl md:block">
        <table class="w-full border-collapse text-left">
          <thead>
            <tr class="border-b border-slate-200 bg-white/60">
              <th class="px-4 py-3 font-display text-xs font-bold uppercase tracking-widest text-navy-600">
                Insumo
              </th>
              <th class="px-4 py-3 font-display text-xs font-bold uppercase tracking-widest text-navy-600">
                Categoría
              </th>
              <th class="px-4 py-3 font-display text-xs font-bold uppercase tracking-widest text-navy-600">
                Unidad
              </th>
              <th class="px-4 py-3 text-right font-display text-xs font-bold uppercase tracking-widest text-navy-600">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="insumo in catalog"
              :key="insumo.id"
              class="border-b border-slate-100 bg-white/40 transition-colors hover:bg-white/70"
              :class="deletingId === insumo.id ? 'opacity-50' : ''"
            >
              <td class="px-4 py-3 text-sm font-semibold text-navy-800">
                {{ insumo.nombre }}
              </td>
              <td class="px-4 py-3">
                <span
                  class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="categoriaColor(insumo.categoria)"
                >
                  {{ categoriaLabel(insumo.categoria) }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-500">{{ insumo.unidad }}</td>
              <td class="px-4 py-3 text-right">
                <button
                  type="button"
                  :disabled="deletingId === insumo.id"
                  class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-display text-xs
                         font-bold uppercase tracking-widest text-red-600 transition-colors
                         hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                  @click="confirmDelete(insumo)"
                >
                  <svg
                    v-if="deletingId === insumo.id"
                    class="h-3.5 w-3.5 animate-spin"
                    viewBox="0 0 24 24"
                    fill="none"
                    aria-hidden="true"
                  >
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z" />
                  </svg>
                  <svg
                    v-else
                    class="h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M3 6h18" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
                    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    <path d="M10 11v6" />
                    <path d="M14 11v6" />
                  </svg>
                  {{ deletingId === insumo.id ? 'Eliminando…' : 'Eliminar' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Cards (mobile) -->
      <ul class="mt-6 flex flex-col gap-3 md:hidden">
        <li
          v-for="insumo in catalog"
          :key="insumo.id"
          class="glass-auth flex items-center justify-between gap-3 rounded-xl p-4"
          :class="deletingId === insumo.id ? 'opacity-50' : ''"
        >
          <div class="min-w-0">
            <h2 class="truncate text-sm font-bold text-navy-800">{{ insumo.nombre }}</h2>
            <div class="mt-1 flex items-center gap-2">
              <span
                class="rounded-full px-2 py-0.5 text-xs font-semibold"
                :class="categoriaColor(insumo.categoria)"
              >
                {{ insumo.categoria }}
              </span>
              <span class="text-xs text-slate-400">{{ insumo.unidad }}</span>
            </div>
          </div>
          <button
            type="button"
            :disabled="deletingId === insumo.id"
            class="inline-flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-1.5 font-display text-xs
                   font-bold uppercase tracking-widest text-red-600 transition-colors
                   hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
            @click="confirmDelete(insumo)"
          >
            <svg
              v-if="deletingId === insumo.id"
              class="h-3.5 w-3.5 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z" />
            </svg>
            {{ deletingId === insumo.id ? 'Eliminando…' : 'Eliminar' }}
          </button>
        </li>
      </ul>
    </template>
  </div>
</template>
