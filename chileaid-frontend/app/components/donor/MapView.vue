<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import MapLegend from '~/components/donor/MapLegend.vue'
import { labelTipoCentro, colorTipoCentro } from '~/utils/tipoCentro'
import { coberturaMarkerColor } from '~/utils/cobertura'
import type { CenterDTO } from '~/services/donorCentersService'

/**
 * VIEW — Mapa interactivo de centros de acopio. Puramente visual: recibe todo
 * por props y comunica intenciones por eventos. No conoce servicios ni
 * composables.
 *
 * Leaflet manipula el DOM y no funciona en SSR, por eso se importa de forma
 * dinámica DENTRO de `onMounted` (nunca en el scope del módulo). El panel lateral
 * reemplaza a los popups nativos de Leaflet. El mapeo cobertura/estado→color es
 * presentación.
 */
const props = defineProps<{
  centers: CenterDTO[]
  selectedCenter: CenterDTO | null
  isLoading: boolean
  error: string | null
}>()

const emit = defineEmits<{
  'select-center': [center: CenterDTO]
  'clear-selection': []
  'go-to-center': [id: string]
  'donate': [id: string]
  'go-back': []
}>()

// Instancia del mapa y marcadores. Tipos vía `import('leaflet')` (solo tipo, se
// borra en compilación); el runtime se carga dinámicamente en onMounted.
let leaflet: typeof import('leaflet') | null = null
let map: import('leaflet').Map | null = null
let markers: import('leaflet').Marker[] = []

/**
 * Color del marcador según estado y cobertura del centro. Delega en el util
 * compartido `coberturaMarkerColor` para que el pin y la leyenda (`MapLegend`)
 * usen exactamente el mismo diccionario de colores.
 */
function getMarkerColor(center: CenterDTO): string {
  return coberturaMarkerColor(center.estado, center.cobertura)
}

/** (Re)dibuja todos los marcadores a partir de props.centers. */
function renderMarkers(): void {
  if (!leaflet || !map) return
  markers.forEach((m) => m.remove())
  markers = []

  for (const center of props.centers) {
    // Sin coordenadas no hay dónde plotear: se omite (evita un pin en [0,0],
    // "Null Island"). Un centro puede quedar sin coords si el geocode falló.
    if (center.latitud == null || center.longitud == null) continue

    const color = getMarkerColor(center)
    const icon = leaflet.divIcon({
      html: `<div style="
        width:16px; height:16px; border-radius:50%;
        background:${color}; border:2px solid white;
        box-shadow:0 1px 4px rgba(0,0,0,0.4);
      "></div>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8],
      className: center.cobertura < 30 ? 'alert-pulse' : ''
    })
    const marker = leaflet
      .marker([center.latitud, center.longitud], { icon })
      .addTo(map)
    marker.on('click', () => emit('select-center', center))
    markers.push(marker)
  }
}

onMounted(async () => {
  // Carga dinámica de Leaflet: nunca en el scope del módulo (rompería el SSR).
  leaflet = await import('leaflet')

  // Mapa centrado en el centro geográfico de Chile; zoom 6 muestra todo el país.
  map = leaflet.map('map').setView([-35.6751, -71.543], 6)

  leaflet
    .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    })
    .addTo(map)

  renderMarkers()

  // Si llegamos con un centro preseleccionado (query ?center=...), enfocarlo.
  if (props.selectedCenter) {
    map.setView(
      [props.selectedCenter.latitud, props.selectedCenter.longitud],
      14
    )
  }
})

onUnmounted(() => {
  map?.remove()
  map = null
})

// Re-dibuja marcadores si cambia la colección de centros.
watch(
  () => props.centers,
  () => renderMarkers()
)

// Centra el mapa cuando cambia la selección (p. ej. al elegir otro centro).
watch(
  () => props.selectedCenter,
  (sel) => {
    if (sel && map) {
      map.setView([sel.latitud, sel.longitud], 14)
    }
  }
)

/** Clase del badge de estado del panel (colores semánticos). */
function badgeClass(center: CenterDTO): string {
  if (center.estado === 'critico') return 'bg-red-100 text-red-700'
  if (center.estado === 'cerrado') return 'bg-slate-100 text-slate-500'
  return center.cobertura >= 70
    ? 'bg-green-100 text-green-700'
    : 'bg-amber-100 text-amber-700'
}

/** Etiqueta legible del estado del centro. */
function badgeLabel(center: CenterDTO): string {
  if (center.estado === 'critico') return 'Crítico'
  if (center.estado === 'cerrado') return 'Cerrado'
  return 'En capacidad'
}

/** Clase Tailwind de la barra de cobertura. */
function barClass(cobertura: number): string {
  if (cobertura >= 70) return 'bg-green-500'
  if (cobertura >= 30) return 'bg-amber-400'
  return 'bg-red-500'
}

/** Ancho de la barra de cobertura, acotado a 0-100. */
function barWidth(cobertura: number): string {
  return `${Math.min(100, Math.max(0, cobertura))}%`
}
</script>

<template>
  <div
    class="flex h-[calc(100vh-5rem)] flex-col bg-[#f0f4ff] md:h-[calc(100vh-3.5rem)]"
  >
    <!-- Header fijo encima del mapa -->
    <header class="shrink-0 px-4 py-3 sm:px-6">
      <button
        type="button"
        class="flex items-center gap-1.5 text-sm font-semibold text-navy-600 hover:text-navy-800"
        @click="emit('go-back')"
      >
        <svg
          class="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M15 18l-6-6 6-6" />
        </svg>
        Volver
      </button>
      <div class="mt-1 flex items-baseline gap-3">
        <h1 class="font-display text-2xl font-black uppercase tracking-wide text-navy-800">
          Mapa de centros
        </h1>
        <span class="text-sm text-slate-500">
          {{ centers.length }}
          {{ centers.length === 1 ? 'centro activo' : 'centros activos' }}
        </span>
      </div>
    </header>

    <!-- Contenedor del mapa (relativo: el panel se superpone) -->
    <div class="relative flex-1">
      <!-- Leaflet se monta sobre este div -->
      <div id="map" class="h-full w-full" />

      <!-- Leyenda/simbología: qué significa cada color de pin y tipo de centro -->
      <MapLegend v-if="!isLoading && !error" />

      <!-- Overlay de carga -->
      <div
        v-if="isLoading"
        class="absolute inset-0 z-[1000] flex items-center justify-center bg-[#f0f4ff]/70"
      >
        <p class="font-display text-sm font-bold uppercase tracking-widest text-navy-800">
          Cargando centros...
        </p>
      </div>

      <!-- Estado de error -->
      <div
        v-else-if="error"
        class="absolute inset-0 z-[1000] flex items-center justify-center px-4"
      >
        <div class="glass-auth max-w-sm rounded-2xl px-6 py-5 text-center shadow-xl">
          <p role="alert" class="text-sm font-semibold text-red-600">
            {{ error }}
          </p>
        </div>
      </div>

      <!-- Panel lateral de detalle -->
      <aside
        v-if="selectedCenter"
        class="glass-auth absolute inset-x-4 bottom-4 z-[1000] rounded-2xl p-5 shadow-xl
               md:inset-x-auto md:bottom-auto md:right-4 md:top-4 md:w-80"
      >
        <!-- Cerrar -->
        <button
          type="button"
          class="absolute right-3 top-3 flex h-7 w-7 items-center justify-center rounded-full
                 text-slate-400 transition-colors hover:bg-navy-800/8 hover:text-navy-800"
          aria-label="Cerrar"
          @click="emit('clear-selection')"
        >
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
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>

        <!-- Badges de estado + tipo de centro -->
        <div class="flex flex-wrap items-center gap-1.5 pr-6">
          <span
            class="inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold"
            :class="badgeClass(selectedCenter)"
          >
            {{ badgeLabel(selectedCenter) }}
          </span>
          <span
            class="inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold"
            :class="colorTipoCentro(selectedCenter.tipoCentro)"
          >
            {{ labelTipoCentro(selectedCenter.tipoCentro) }}
          </span>
        </div>

        <!-- Nombre + organización -->
        <h2 class="mt-2 pr-6 font-display text-lg font-black uppercase leading-tight text-navy-800">
          {{ selectedCenter.nombre }}
        </h2>
        <p class="mt-1 text-sm text-slate-500">
          {{ selectedCenter.organizacion }}
        </p>
        <p class="mt-0.5 text-sm text-slate-500">
          {{ selectedCenter.direccion }}
        </p>
        <!-- Emergencia específica a la que responde el centro -->
        <span
          v-if="selectedCenter.emergenciaNombre"
          class="mt-2 inline-flex items-center gap-1.5 rounded-full bg-navy-800/8 px-2.5 py-1
                 text-xs font-semibold text-navy-800"
        >
          <svg
            class="h-3.5 w-3.5 shrink-0"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <path d="M12 9v4" />
            <path d="M12 17h.01" />
          </svg>
          {{ selectedCenter.emergenciaNombre }}
        </span>

        <!-- Barra de cobertura -->
        <div class="mt-4">
          <div class="h-2 w-full overflow-hidden rounded-full bg-navy-800/8">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="barClass(selectedCenter.cobertura)"
              :style="{ width: barWidth(selectedCenter.cobertura) }"
            />
          </div>
          <p class="mt-1.5 text-sm font-semibold text-navy-800">
            Cobertura {{ selectedCenter.cobertura }}%
          </p>
        </div>

        <!-- Necesidades urgentes como chips -->
        <div
          v-if="selectedCenter.necesidadesUrgentes.length > 0"
          class="mt-4 flex flex-wrap gap-1.5"
        >
          <span
            v-for="need in selectedCenter.necesidadesUrgentes"
            :key="need"
            class="rounded bg-navy-800/8 px-2 py-1 text-xs text-navy-800"
          >
            {{ need }}
          </span>
        </div>

        <!-- Donar: CTA principal. Se oculta en centros cerrados (meta cumplida,
             ya no reciben donaciones). Sin sesión, el middleware de la ruta de
             donación difiere el login y devuelve al flujo tras autenticar. -->
        <BaseButton
          v-if="selectedCenter.estado !== 'cerrado'"
          variant="navy"
          full-width
          class="mt-5"
          @click="emit('donate', selectedCenter.id)"
        >
          Donar
        </BaseButton>

        <!-- Ver detalle completo -->
        <BaseButton
          variant="ghost"
          full-width
          :class="selectedCenter.estado !== 'cerrado' ? 'mt-2' : 'mt-5'"
          @click="emit('go-to-center', selectedCenter.id)"
        >
          Ver detalle completo
        </BaseButton>
      </aside>
    </div>
  </div>
</template>
