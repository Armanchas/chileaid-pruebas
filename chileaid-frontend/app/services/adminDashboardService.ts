/**
 * MODEL — Capa de acceso a datos del panel de administración de la plataforma.
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`):
 *   getPlatformStats  → `GET /admin/stats`    (agregados globales, role=admin)
 *   getRecentActivity → `GET /admin/activity` (feed de eventos de organizaciones)
 *
 * Visión global de la plataforma: organizaciones (activas/pendientes de revisión),
 * donaciones, emergencias activas, centros operativos y entregas realizadas.
 */
import { apiFetch } from '~/utils/apiFetch'

/** Métricas agregadas del estado general de la plataforma Chile Aid. */
export interface PlatformStatsDTO {
  organizacionesActivas: number
  organizacionesPendientes: number
  donacionesTotales: number
  donacionesUltimos7Dias: number
  emergenciasActivas: number
  centrosOperativos: number
  /** Nº de salidas de distribución (COUNT de lotes), no suma de cantidades. */
  entregasRealizadas: number
}

/**
 * Evento reciente del feed de actividad de la plataforma. El admin monitorea el
 * ciclo de vida de las ORGANIZACIONES (alta y moderación); por eso el feed solo
 * incluye eventos de organización, no de donaciones ni emergencias.
 */
export interface RecentActivityItem {
  id: string
  tipo: 'org_registrada' | 'org_aprobada' | 'org_rechazada'
  descripcion: string
  /** Fecha ISO `YYYY-MM-DD`. */
  fecha: string
}

export const adminDashboardService = {
  /** Métricas globales de la plataforma (`GET /admin/stats`, agregados server-side). */
  async getPlatformStats(): Promise<PlatformStatsDTO> {
    return apiFetch<PlatformStatsDTO>('/admin/stats')
  },

  /** Eventos recientes de organizaciones (`GET /admin/activity`), recientes primero. */
  async getRecentActivity(): Promise<RecentActivityItem[]> {
    return apiFetch<RecentActivityItem[]>('/admin/activity', {
      query: { orden: 'fecha_desc' }
    })
  }
}
