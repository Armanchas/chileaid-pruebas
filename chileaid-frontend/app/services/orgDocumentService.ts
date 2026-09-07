/**
 * MODEL — Capa de acceso a datos para documentos de respaldo de la org (RF-03).
 *
 * Flujo de subida en dos pasos:
 *  1. `getUploadUrl`  → POST /org/documents/upload-url  → presigned POST de S3
 *  2. `uploadToS3`    → POST directo al endpoint S3 con FormData (sin pasar por FastAPI)
 *  3. `saveDocument`  → POST /org/documents             → guarda el registro en BD
 *
 * `listDocuments` → GET /org/documents → lista con URLs firmadas de descarga.
 */
import { apiFetch } from '~/utils/apiFetch'

export interface OrgDocumentDTO {
  id: string
  nombreArchivo: string
  tipo: string
  url: string // presigned download URL (expira en 1 h)
}

export interface PresignedPost {
  url: string
  fields: Record<string, string>
}

export interface UploadURLResponse {
  presignedPost: PresignedPost
  objectKey: string
}

export const orgDocumentService = {
  async listDocuments(): Promise<OrgDocumentDTO[]> {
    return apiFetch<OrgDocumentDTO[]>('/org/documents')
  },

  /**
   * `authToken` es opcional y solo se usa fuera de una sesión persistida —el
   * registro de organización lo pasa con el JWT recién emitido para subir el
   * documento de respaldo antes de navegar a /login (§CU-01).
   */
  async getUploadUrl(
    nombreArchivo: string,
    tipo: string,
    authToken?: string
  ): Promise<UploadURLResponse> {
    return apiFetch<UploadURLResponse>(
      '/org/documents/upload-url',
      { method: 'POST', body: { nombreArchivo, tipo } },
      authToken
    )
  },

  /** Sube el archivo directamente al bucket S3 usando la URL presignada. */
  async uploadToS3(presignedPost: PresignedPost, file: File): Promise<void> {
    const form = new FormData()
    for (const [key, val] of Object.entries(presignedPost.fields)) {
      form.append(key, val)
    }
    form.append('file', file)
    const res = await fetch(presignedPost.url, { method: 'POST', body: form })
    if (!res.ok) {
      throw new Error('Error al subir el archivo al storage. Inténtalo de nuevo.')
    }
  },

  async saveDocument(
    nombreArchivo: string,
    objectKey: string,
    tipo: string,
    authToken?: string
  ): Promise<OrgDocumentDTO> {
    return apiFetch<OrgDocumentDTO>(
      '/org/documents',
      { method: 'POST', body: { nombreArchivo, objectKey, tipo } },
      authToken
    )
  }
}
