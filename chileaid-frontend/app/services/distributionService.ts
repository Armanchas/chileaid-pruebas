/**
 * MODEL — Capa de acceso a datos de la distribución/inventario de la organización
 * receptora (salida de insumos: a terreno o a beneficiarios).
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`):
 *   getStock  → `GET  /org/stock`   (derivado: recibido − distribuido)
 *   getLots   → `GET  /org/lots`
 *   createLot → `POST /org/lots`
 *
 * El **stock** es derivado server-side (no se persiste); un **lote** es una salida
 * ya registrada (hecho inmutable, sin ciclo de estados). El contrato se keyea por
 * `insumoId` (UUID), no por nombre. La salida disponible (`tipo`) depende del tipo
 * de centro (`OrgType`) — el backend lo valida además del filtro en cliente.
 */
import { apiFetch } from '~/utils/apiFetch'
import type { OrgTipoCentro } from '~/services/orgDashboardService'

/**
 * Tipo de centro de la organización. Alias del ya definido en el panel
 * (`OrgTipoCentro`): se reutiliza para no duplicar la unión literal.
 */
export type OrgType = OrgTipoCentro

/** Acción de salida de un lote: a terreno o entregado a un beneficiario. */
export type LotSalida = 'enviado_a_terreno' | 'entregado_a_beneficiario'

/** Lote ya distribuido: una salida de stock registrada. */
export interface DistributionLotDTO {
  id: string
  insumoId: string
  categoria: string
  insumoNombre: string
  cantidad: number
  unidad: string
  tipo: LotSalida
  destino: string
  fecha: string
}

/** Datos que el formulario envía para registrar una nueva salida de stock. */
export interface CreateLotInput {
  insumoId: string
  cantidad: number
  tipo: LotSalida
  destino: string
}

/** Stock disponible de un insumo (recibido − ya distribuido). */
export interface StockItem {
  insumoId: string
  insumoNombre: string
  categoria: string
  unidad: string
  cantidadDisponible: number
}

/**
 * Extrae un mensaje legible del error que lanza `apiFetch`/`$fetch`. FastAPI
 * responde `{ detail }`: string en los `HTTPException` de negocio (404/422 stock
 * insuficiente / gating) o un array en los 422 de validación de Pydantic.
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

export const distributionService = {
  /** Lotes ya distribuidos del centro (`GET /org/lots`), recientes primero. */
  async getLots(): Promise<DistributionLotDTO[]> {
    return apiFetch<DistributionLotDTO[]>('/org/lots')
  },

  /** Stock disponible por insumo (`GET /org/stock`, derivado server-side). */
  async getStock(): Promise<StockItem[]> {
    return apiFetch<StockItem[]>('/org/stock')
  },

  /**
   * Registra una nueva salida de stock (`POST /org/lots`). El backend valida el
   * stock disponible y el gating por tipo de centro; un 4xx (422 stock
   * insuficiente / tipo no permitido, 404 insumo/centro) se relanza como `Error`
   * con el `detail` para que el ViewModel lo muestre sin cerrar el modal.
   */
  async createLot(input: CreateLotInput): Promise<DistributionLotDTO> {
    try {
      return await apiFetch<DistributionLotDTO>('/org/lots', {
        method: 'POST',
        body: {
          insumoId: input.insumoId,
          cantidad: input.cantidad,
          tipo: input.tipo,
          destino: input.destino
        }
      })
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo registrar la salida.'))
    }
  }
}
