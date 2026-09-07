import { computed, ref } from 'vue'
import {
  adminDashboardService,
  type PlatformStatsDTO,
  type RecentActivityItem
} from '~/services/adminDashboardService'

/**
 * VIEW-MODEL — Puente reactivo entre el panel de administración y el modelo.
 *
 * Es el ÚNICO punto de la app que habla con `adminDashboardService`. Expone estado
 * reactivo (ref/computed) y las intenciones de navegación (`goOrgs`, `goCatalog`);
 * los componentes nunca tocan el servicio, solo consumen lo que aquí se publica
 * vía props desde la página.
 */
export function useAdminDashboardViewModel() {
  const stats = ref<PlatformStatsDTO | null>(null)
  const recentActivity = ref<RecentActivityItem[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  /**
   * Porcentaje de organizaciones pendientes sobre el total (activas + pendientes).
   * Retorna 0 si no hay organizaciones para evitar dividir por cero.
   */
  const tasaPendientes = computed<number>(() => {
    const activas = stats.value?.organizacionesActivas ?? 0
    const pendientes = stats.value?.organizacionesPendientes ?? 0
    const total = activas + pendientes
    return total === 0 ? 0 : Math.round((pendientes / total) * 100)
  })

  /** Etiqueta legible para el tipo de un evento de actividad (solo organizaciones). */
  function actividadLabel(tipo: string): string {
    const labels: Record<string, string> = {
      org_registrada: 'Nueva organización',
      org_aprobada: 'Organización aprobada',
      org_rechazada: 'Organización rechazada'
    }
    return labels[tipo] ?? tipo
  }

  /** Clases del badge (color) para el tipo de un evento de actividad. */
  function actividadColor(tipo: string): string {
    const colors: Record<string, string> = {
      org_registrada: 'bg-blue-100 text-blue-800',
      org_aprobada: 'bg-green-100 text-green-700',
      org_rechazada: 'bg-red-100 text-red-700'
    }
    return colors[tipo] ?? 'bg-slate-100 text-slate-600'
  }

  /**
   * Carga en paralelo las métricas globales y la actividad reciente. Maneja los
   * estados de carga y error de forma centralizada.
   */
  async function loadDashboard(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [statsData, activityData] = await Promise.all([
        adminDashboardService.getPlatformStats(),
        adminDashboardService.getRecentActivity()
      ])
      stats.value = statsData
      recentActivity.value = activityData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'No se pudo cargar el panel.'
    } finally {
      isLoading.value = false
    }
  }

  /** Navega a la revisión de organizaciones. */
  function goOrgs(): void {
    navigateTo('/admin/orgs')
  }

  /** Navega a la gestión del catálogo de insumos. */
  function goCatalog(): void {
    navigateTo('/admin/catalog')
  }

  return {
    // estado
    stats,
    recentActivity,
    isLoading,
    error,
    // derivados
    tasaPendientes,
    // mapeos puros
    actividadLabel,
    actividadColor,
    // acciones
    loadDashboard,
    goOrgs,
    goCatalog
  }
}
