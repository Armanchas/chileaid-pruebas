<script setup lang="ts">
import { onMounted, onUnmounted, nextTick, watch } from 'vue'

/**
 * VIEW — Selector de ubicación en un mini-mapa (RF-05). Puramente visual: recibe
 * el punto actual por props y emite `pick` cuando la org hace click o arrastra el
 * pin. No conoce servicios ni composables (la geocodificación por dirección la
 * resuelve el `OrgCenterForm` vía una prop-función del ViewModel).
 *
 * Leaflet manipula el DOM y no corre en SSR, por eso se importa dinámicamente
 * DENTRO de `onMounted`. El CSS de Leaflet lo carga el plugin `leaflet.client.ts`.
 */
const props = defineProps<{
  latitud: number | null
  longitud: number | null
}>()

const emit = defineEmits<{ pick: [{ latitud: number; longitud: number }] }>()

// Centro geográfico de Chile: encuadre inicial cuando aún no hay punto elegido.
const FALLBACK: [number, number] = [-35.6751, -71.543]

let leaflet: typeof import('leaflet') | null = null
let map: import('leaflet').Map | null = null
let marker: import('leaflet').Marker | null = null

/** Redondea a 6 decimales, alineado con `Numeric(9,6)` del backend. */
function round(n: number): number {
  return Math.round(n * 1e6) / 1e6
}

function hasCoords(): boolean {
  return props.latitud != null && props.longitud != null
}

/**
 * Pin como punto dibujado por CSS (`divIcon`), NO el marcador por defecto de
 * Leaflet: su icono PNG (`marker-icon.png`) se sirve por una URL que el bundler
 * de Nuxt no resuelve, y aparecía como imagen rota. Mismo enfoque que `MapView`.
 */
function buildPinIcon() {
  return leaflet!.divIcon({
    html: `<div style="
      width:18px; height:18px; border-radius:50%;
      background:#0039a6; border:2px solid white;
      box-shadow:0 1px 4px rgba(0,0,0,0.4);
    "></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    className: ''
  })
}

/** Coloca (o mueve) el pin arrastrable en el punto dado. */
function placeMarker(lat: number, lng: number): void {
  if (!leaflet || !map) return
  if (marker) {
    marker.setLatLng([lat, lng])
    return
  }
  marker = leaflet
    .marker([lat, lng], { draggable: true, icon: buildPinIcon() })
    .addTo(map)
  marker.on('dragend', () => {
    const p = marker!.getLatLng()
    emit('pick', { latitud: round(p.lat), longitud: round(p.lng) })
  })
}

onMounted(async () => {
  leaflet = await import('leaflet')
  const start: [number, number] = hasCoords()
    ? [props.latitud as number, props.longitud as number]
    : FALLBACK
  map = leaflet.map('org-location-map').setView(start, hasCoords() ? 15 : 5)
  leaflet
    .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    })
    .addTo(map)

  if (hasCoords()) {
    placeMarker(props.latitud as number, props.longitud as number)
  }

  // Click en el mapa = elegir/mover el punto.
  map.on('click', (e: import('leaflet').LeafletMouseEvent) => {
    const lat = round(e.latlng.lat)
    const lng = round(e.latlng.lng)
    placeMarker(lat, lng)
    emit('pick', { latitud: lat, longitud: lng })
  })

  // El mapa se monta dentro de un modal recién visible: recalcular su tamaño
  // tras el layout evita que Leaflet renderice con 0px (tiles grises).
  await nextTick()
  map.invalidateSize()
})

onUnmounted(() => {
  map?.remove()
  map = null
  marker = null
})

// Refleja cambios externos del punto (geocodificado por dirección o editado a
// mano en los inputs de lat/lng): recentra y mueve el pin, o lo quita si se
// vaciaron las coordenadas.
watch(
  [() => props.latitud, () => props.longitud],
  ([lat, lng]) => {
    if (!map) return
    if (lat != null && lng != null) {
      placeMarker(lat, lng)
      map.setView([lat, lng], Math.max(map.getZoom() ?? 0, 14))
    } else if (marker) {
      marker.remove()
      marker = null
    }
  }
)
</script>

<template>
  <div
    id="org-location-map"
    class="h-48 w-full overflow-hidden rounded-lg ring-1 ring-navy-600/20"
    style="z-index: 0"
  />
</template>
