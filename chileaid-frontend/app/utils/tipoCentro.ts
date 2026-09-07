/**
 * Helpers de presentación para el tipo de centro
 * (`centro_acopio` / `punto_distribucion` / `ambos`). Lógica de UI compartida
 * por las vistas del donante (tarjeta, detalle y panel del mapa) para no
 * duplicar el mapeo etiqueta/color en cada componente.
 */

/** Valores posibles del tipo de centro, en orden de presentación (para la leyenda). */
export const TIPOS_CENTRO = ['centro_acopio', 'punto_distribucion', 'ambos'] as const

/** Etiqueta legible del tipo de centro. */
export function labelTipoCentro(tipo: string): string {
  if (tipo === 'centro_acopio') return 'Centro de acopio'
  if (tipo === 'punto_distribucion') return 'Punto de distribución'
  return 'Acopio y distribución'
}

/** Clases Tailwind del badge según el tipo de centro. */
export function colorTipoCentro(tipo: string): string {
  if (tipo === 'centro_acopio') return 'bg-blue-100 text-blue-800'
  if (tipo === 'punto_distribucion') return 'bg-teal-100 text-teal-800'
  return 'bg-purple-100 text-purple-700'
}

/** Texto explicativo del rol del centro (usado en el detalle). */
export function descripcionTipoCentro(tipo: string): string {
  if (tipo === 'centro_acopio') return 'Recibe donaciones físicas'
  if (tipo === 'punto_distribucion') return 'Entrega ayuda a personas'
  return 'Recibe y entrega ayuda'
}
