/**
 * MODEL — Capa de acceso a datos de la gestión del CATÁLOGO de insumos por el
 * administrador.
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`):
 *   getCatalog   → `GET /admin/catalog`     (solo insumos activos)
 *   createInsumo → `POST /admin/catalog`    (alta; reactiva un soft-deleted)
 *   deleteInsumo → `DELETE /admin/catalog/{id}` (baja lógica)
 *
 * El catálogo es la misma lista que consumen las orgs (`GET /org/catalog/insumos`);
 * el backend persiste altas/bajas (soft-delete con flag `activo`). El DTO se
 * reutiliza de `orgNeedsService`.
 */
import { apiFetch } from '~/utils/apiFetch'
import { type InsumoCatalogDTO } from '~/services/orgNeedsService'

// Reutiliza el contrato del catálogo: mismo DTO en todo el dominio.
export type { InsumoCatalogDTO }

/** Datos que el formulario envía para dar de alta un insumo en el catálogo. */
export interface CreateInsumoInput {
  nombre: string
  /** value del enum InsumoCategory del backend (minúscula). */
  categoria: string
  unidad: string
}

/** Resultado tipado de una acción del administrador sobre el catálogo. */
export interface CatalogActionResult {
  success: boolean
  error?: string
}

/**
 * Categorías del catálogo: `value` calza EXACTAMENTE con el enum `InsumoCategory`
 * del backend (lo que viaja en `categoria`); `label` es el texto que ve el admin.
 * El `<select>` del modal envía el `value`.
 */
export const CATEGORIAS_INSUMO = [
  { value: 'agua', label: 'Agua' },
  { value: 'alimentos', label: 'Alimentos' },
  { value: 'ropa', label: 'Ropa' },
  { value: 'abrigo', label: 'Abrigo' },
  { value: 'higiene', label: 'Higiene' },
  { value: 'medicamentos', label: 'Medicamentos' },
  { value: 'otros', label: 'Otros' }
] as const

/** Unidades de medida disponibles para un insumo del catálogo (texto libre). */
export const UNIDADES_INSUMO = [
  'unidades',
  'kg',
  'litros',
  'prendas',
  'pares',
  'kits',
  'cajas',
  'metros'
] as const

/**
 * Extrae un mensaje legible del error que lanza `apiFetch`/`$fetch`. FastAPI
 * responde `{ detail }`: un string en los `HTTPException` de negocio (409
 * duplicado / en uso) o un array en los 422 de validación de Pydantic.
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

export const adminCatalogService = {
  /** Catálogo completo de insumos ACTIVOS (`GET /admin/catalog`). */
  async getCatalog(): Promise<InsumoCatalogDTO[]> {
    return apiFetch<InsumoCatalogDTO[]>('/admin/catalog')
  },

  /**
   * Da de alta un insumo (`POST /admin/catalog`). Si el backend rechaza (409
   * nombre duplicado, 422 validación) se relanza un `Error` con el mensaje
   * legible, para que el ViewModel lo muestre en el modal de alta.
   */
  async createInsumo(input: CreateInsumoInput): Promise<InsumoCatalogDTO> {
    try {
      return await apiFetch<InsumoCatalogDTO>('/admin/catalog', {
        method: 'POST',
        body: {
          nombre: input.nombre,
          categoria: input.categoria,
          unidad: input.unidad
        }
      })
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo agregar el insumo.'))
    }
  },

  /**
   * Da de baja un insumo (`DELETE /admin/catalog/{id}`, soft-delete). NO lanza:
   * devuelve `{ success:false, error }` si el backend responde 409 (insumo en
   * uso por necesidades activas) o 404, para que el ViewModel decida.
   */
  async deleteInsumo(id: string): Promise<CatalogActionResult> {
    try {
      await apiFetch(`/admin/catalog/${id}`, { method: 'DELETE' })
      return { success: true }
    } catch (err) {
      return {
        success: false,
        error: apiErrorMessage(err, 'No se pudo eliminar el insumo.')
      }
    }
  }
}
