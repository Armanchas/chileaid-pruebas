/**
 * PLUGIN (solo cliente) — Registra los estilos de Leaflet.
 *
 * El sufijo `.client.ts` hace que Nuxt lo cargue únicamente en el navegador:
 * Leaflet manipula el DOM y no funciona en SSR. Aquí solo importamos su CSS para
 * que las tiles y los controles del mapa se vean correctamente; la librería en
 * sí se importa dinámicamente dentro de `onMounted` en el componente del mapa.
 *
 * Importante: este es el ÚNICO lugar donde se importa `leaflet/dist/leaflet.css`.
 */
import 'leaflet/dist/leaflet.css'

export default defineNuxtPlugin(() => {})
