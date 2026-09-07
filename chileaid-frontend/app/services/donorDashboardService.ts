/**
 * MODEL — Catálogo estático de regiones de Chile.
 *
 * El acceso a datos de centros/emergencias del donante migró a
 * `donorCentersService.ts` (conectado al backend real). Este módulo conserva
 * únicamente `REGIONES_CHILE`, un catálogo estático compartido por el selector de
 * región del registro/perfil de organización y por el filtro del listado de
 * centros. No proviene de la API.
 */

/**
 * Listado fijo de las 16 regiones de Chile (más la opción neutra `Todas las
 * regiones`, que en los filtros significa "sin restricción").
 */
export const REGIONES_CHILE: string[] = [
  'Todas las regiones',
  'Arica y Parinacota',
  'Tarapacá',
  'Antofagasta',
  'Atacama',
  'Coquimbo',
  'Valparaíso',
  'Metropolitana',
  "O'Higgins",
  'Maule',
  'Ñuble',
  'Biobío',
  'La Araucanía',
  'Los Ríos',
  'Los Lagos',
  'Aysén',
  'Magallanes'
]
