/**
 * MODEL — Capa de acceso a datos de la gestión de organizaciones del administrador.
 *
 * Conectado al backend real vía `apiFetch`:
 *   getOrgs        → GET  /admin/orgs (paginado)
 *   getOrgCounts   → GET  /admin/orgs/counts
 *   approveOrg     → POST /admin/orgs/{id}/approve
 *   rejectOrg      → POST /admin/orgs/{id}/reject
 *   deactivateOrg  → POST /admin/orgs/{id}/deactivate
 *   reactivateOrg  → POST /admin/orgs/{id}/reactivate
 */
import { apiFetch } from '~/utils/apiFetch'
import type { OrgType, OrgEstado } from '~/services/orgProfileService'

/** Envelope de paginación genérico (espejo de `Page[T]` del backend). */
export interface Page<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

/** Conteo de organizaciones por estado (pestañas del panel admin). */
export interface AdminOrgCountsDTO {
  todas: number
  pendiente: number
  activa: number
  rechazada: number
  inactiva: number
}

/** Organización vista desde el panel del administrador (datos completos). */
export interface AdminOrgDTO {
  id: string
  nombre: string
  tipo: OrgType
  rut: string | null
  contactoNombre: string | null
  email: string
  telefono: string | null
  region: string | null
  documentacion: string
  estado: OrgEstado
  fechaRegistro: string // ISO YYYY-MM-DD
  motivoRechazo: string | null
}

/** Documento de respaldo de una organización, visto desde el panel del admin. */
export interface AdminDocumentDTO {
  id: string
  nombreArchivo: string
  tipo: string
  url: string // presigned download URL (expira en 1 h)
}

/** Resultado tipado de una acción del administrador sobre una organización. */
export interface OrgActionResult {
  success: boolean
  error?: string
}

function apiErrorMessage(err: unknown, fallback: string): string {
  const detail = (err as { data?: { detail?: unknown } })?.data?.detail
  if (typeof detail === 'string') return detail
  return fallback
}

export const adminOrgsService = {
  /** Página de organizaciones, con filtro opcional por estado. */
  async getOrgs(params: {
    estado?: OrgEstado | 'todas'
    limit: number
    offset: number
  }): Promise<Page<AdminOrgDTO>> {
    const { estado, limit, offset } = params
    return apiFetch<Page<AdminOrgDTO>>('/admin/orgs', {
      query: {
        ...(estado && estado !== 'todas' ? { estado } : {}),
        limit,
        offset
      }
    })
  },

  /** Conteo por estado, independiente de la paginación del listado. */
  async getOrgCounts(): Promise<AdminOrgCountsDTO> {
    return apiFetch<AdminOrgCountsDTO>('/admin/orgs/counts')
  },

  async approveOrg(id: string): Promise<OrgActionResult> {
    try {
      await apiFetch(`/admin/orgs/${id}/approve`, { method: 'POST' })
      return { success: true }
    } catch (err) {
      return { success: false, error: apiErrorMessage(err, 'No se pudo aprobar la organización.') }
    }
  },

  async rejectOrg(id: string): Promise<OrgActionResult> {
    try {
      await apiFetch(`/admin/orgs/${id}/reject`, { method: 'POST' })
      return { success: true }
    } catch (err) {
      return { success: false, error: apiErrorMessage(err, 'No se pudo rechazar la organización.') }
    }
  },

  async deactivateOrg(id: string): Promise<OrgActionResult> {
    try {
      await apiFetch(`/admin/orgs/${id}/deactivate`, { method: 'POST' })
      return { success: true }
    } catch (err) {
      return { success: false, error: apiErrorMessage(err, 'No se pudo desactivar la organización.') }
    }
  },

  async reactivateOrg(id: string): Promise<OrgActionResult> {
    try {
      await apiFetch(`/admin/orgs/${id}/reactivate`, { method: 'POST' })
      return { success: true }
    } catch (err) {
      return { success: false, error: apiErrorMessage(err, 'No se pudo reactivar la organización.') }
    }
  },

  async getOrgDocuments(id: string): Promise<AdminDocumentDTO[]> {
    return apiFetch<AdminDocumentDTO[]>(`/admin/orgs/${id}/documents`)
  }
}
