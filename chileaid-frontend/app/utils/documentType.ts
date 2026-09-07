/**
 * Resuelve el `tipo` de documento de respaldo (RF-03) a partir de la
 * extensión del archivo. Compartido por el registro de organización y la
 * sección de documentos del perfil para no duplicar la lista de extensiones
 * aceptadas.
 */

const EXTENSIONES_ACEPTADAS = ['pdf', 'jpg', 'jpeg'] as const

export type DocumentoTipo = 'pdf' | 'jpg'

/** `null` si la extensión no es pdf/jpg/jpeg. */
export function resolveDocumentTipo(nombreArchivo: string): DocumentoTipo | null {
  const extension = nombreArchivo.split('.').pop()?.toLowerCase() ?? ''
  if (!EXTENSIONES_ACEPTADAS.includes(extension as (typeof EXTENSIONES_ACEPTADAS)[number])) {
    return null
  }
  return extension === 'pdf' ? 'pdf' : 'jpg'
}
