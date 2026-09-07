/**
 * Helpers de presentación de la cobertura de un centro. Fuente ÚNICA del color
 * del marcador del mapa, compartida por `MapView` (que lo inyecta como hex en el
 * `divIcon` de Leaflet) y por `MapLegend` (los swatches de la leyenda), para que
 * la simbología y los pines nunca se desincronicen.
 *
 * ⚠️ Naming: este concepto se llama SIEMPRE "cobertura", nunca "saturación".
 */

/** Color hex del marcador según estado y cobertura del centro. */
export function coberturaMarkerColor(estado: string, cobertura: number): string {
  if (estado === 'cerrado') return '#94a3b8' // slate
  if (cobertura < 30) return '#dc2626' // rojo
  if (cobertura < 70) return '#d97706' // ámbar
  return '#16a34a' // verde
}

/** Una entrada de la leyenda de cobertura (swatch + qué significa). */
export interface CoberturaLegendItem {
  /** Color hex, idéntico al del pin en el mapa. */
  color: string
  label: string
  hint: string
}

/**
 * Diccionario de la leyenda de cobertura, en orden de gravedad. Los colores
 * coinciden 1:1 con lo que devuelve `coberturaMarkerColor`, así la leyenda
 * describe exactamente los pines que el usuario ve.
 */
export const COBERTURA_LEGEND: CoberturaLegendItem[] = [
  { color: '#dc2626', label: 'Crítico', hint: 'sin cobertura, necesita todo' },
  { color: '#d97706', label: 'Cobertura parcial', hint: 'tiene parte de lo que necesita' },
  { color: '#16a34a', label: 'Buena cobertura', hint: 'cerca de su meta' },
  { color: '#94a3b8', label: 'Cerrado', hint: 'meta cumplida, no recibe más' }
]
