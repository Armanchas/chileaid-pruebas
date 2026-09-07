/**
 * MODEL — Capa de acceso a datos de la gestión de necesidades de la organización
 * receptora (CU "Gestionar Necesidades").
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`):
 *   getInsumosCatalog → `GET   /org/catalog/insumos`  (IDs reales del catálogo)
 *   getOrgNeeds       → `GET   /org/needs`
 *   createOrgNeed     → `POST  /org/needs`
 *   updateOrgNeed     → `PUT   /org/needs/{id}`
 *   closeOrgNeed      → `PATCH /org/needs/{id}/cerrar`  (cierre manual, CU-03)
 *
 * Todas devuelven el `NeedDTO` UNIFICADO (definido en `orgDashboardService`,
 * misma forma que `necesidades` en `/org/center`): el backend ya entrega esa
 * forma, así que NO hay capa de mapeo de salida. Ya no quedan mocks en este
 * service.
 */

import { apiFetch } from '~/utils/apiFetch'
import type { NeedDTO, Urgencia } from '~/services/orgDashboardService'

/** Ítem del catálogo de insumos que la organización puede solicitar. */
export interface InsumoCatalogDTO {
  id: string
  nombre: string
  categoria: string
  unidad: string
}

/** Datos que el formulario envía para publicar una nueva necesidad. */
export interface CreateNeedInput {
  insumoId: string
  cantidadRequerida: number
  urgencia: Urgencia
}

/**
 * Datos editables de una necesidad existente. El insumo NO se puede cambiar: solo
 * la cantidad requerida y la urgencia.
 */
export interface UpdateNeedInput {
  cantidadRequerida: number
  urgencia: Urgencia
}

/**
 * Extrae un mensaje legible del error que lanza `apiFetch`/`$fetch`. FastAPI
 * responde `{ detail }`: un string en nuestros `HTTPException` de negocio
 * (404 sin centro / insumo, 422 de cantidad) o un array en los 422 de validación
 * de Pydantic. Cae al `fallback` si no hay forma reconocible.
 */
function apiErrorMessage(err: unknown, fallback: string): string {
  const detail = (err as { data?: { detail?: unknown } })?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string }
    if (typeof first?.msg === 'string') return first.msg
  }
  return fallback
}

export const orgNeedsService = {
  /**
   * Devuelve el catálogo de insumos solicitables (`GET /org/catalog/insumos`),
   * con sus IDs REALES (UUID): son los que el alta envía como `insumoId`.
   */
  async getInsumosCatalog(): Promise<InsumoCatalogDTO[]> {
    return apiFetch<InsumoCatalogDTO[]>('/org/catalog/insumos')
  },

  /**
   * Devuelve las necesidades de la organización (`GET /org/needs`). El backend
   * resuelve la org desde el JWT y devuelve `[]` si no tiene centro.
   */
  async getOrgNeeds(): Promise<NeedDTO[]> {
    return apiFetch<NeedDTO[]>('/org/needs')
  },

  /**
   * Publica una nueva necesidad (`POST /org/needs`).
   *
   * NO hace falta mapear el payload: el backend espera EXACTAMENTE
   * `{ insumoId, cantidadRequerida, urgencia }` y el formulario ya provee un
   * `insumoId` real del catálogo + la urgencia como enum string de 3 niveles
   * (post Task 2). La respuesta ya es el `NeedDTO` unificado → se retorna tal cual.
   * Un 4xx (sin centro, insumo inexistente, validación) se traduce a un `Error`
   * con el `detail` del backend para que el VM lo muestre en el modal.
   */
  async createOrgNeed(input: CreateNeedInput): Promise<NeedDTO> {
    try {
      return await apiFetch<NeedDTO>('/org/needs', {
        method: 'POST',
        body: {
          insumoId: input.insumoId,
          cantidadRequerida: input.cantidadRequerida,
          urgencia: input.urgencia
        }
      })
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo publicar la necesidad.'))
    }
  },

  /**
   * Actualiza la cantidad requerida y la urgencia de una necesidad existente
   * (`PUT /org/needs/{id}`); el insumo no se cambia. Respuesta = `NeedDTO`
   * unificado. Propaga el `detail` del backend como `Error` legible.
   */
  async updateOrgNeed(id: string, data: UpdateNeedInput): Promise<NeedDTO> {
    try {
      return await apiFetch<NeedDTO>(`/org/needs/${id}`, {
        method: 'PUT',
        body: {
          cantidadRequerida: data.cantidadRequerida,
          urgencia: data.urgencia
        }
      })
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo actualizar la necesidad.'))
    }
  },

  /**
   * Cierre manual de una necesidad (`PATCH /org/needs/{id}/cerrar`, CU-03): la
   * marca como `cerrada` para que no reciba nuevos aportes (no revierte lo ya
   * comprometido/recibido). Devuelve el `NeedDTO` actualizado. El backend
   * responde 409 si no está `activa` y 404 si no existe/no es del centro de la
   * org; se propaga el `detail` como `Error` legible.
   */
  async closeOrgNeed(id: string): Promise<NeedDTO> {
    try {
      return await apiFetch<NeedDTO>(`/org/needs/${id}/cerrar`, { method: 'PATCH' })
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo cerrar la necesidad.'))
    }
  }
}
