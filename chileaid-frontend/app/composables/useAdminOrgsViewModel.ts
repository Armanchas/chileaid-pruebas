import { computed, ref } from 'vue'
import {
  adminOrgsService,
  type AdminDocumentDTO,
  type AdminOrgCountsDTO,
  type AdminOrgDTO
} from '~/services/adminOrgsService'
import type { OrgType, OrgEstado } from '~/services/orgProfileService'

/** Filtro de la lista: cualquier estado o el comodín `todas`. */
type FiltroEstado = OrgEstado | 'todas'

const PAGE_SIZE = 20

const COUNTS_VACIOS: AdminOrgCountsDTO = {
  todas: 0,
  pendiente: 0,
  activa: 0,
  rechazada: 0,
  inactiva: 0
}

/**
 * VIEW-MODEL — Puente reactivo de la gestión de organizaciones del administrador
 * (`/admin/orgs`).
 *
 * Es el ÚNICO punto que habla con `adminOrgsService`. Carga la página actual
 * (paginada server-side), mantiene el filtro por estado, el detalle seleccionado
 * y orquesta las acciones de moderación (aprobar/rechazar/desactivar/reactivar).
 * Las vistas solo consumen estado/derivados por props y emiten intenciones. El
 * mapeo de etiquetas/colores de `estado` y `tipo` es presentación derivada
 * (misma lógica que `useOrgProfileViewModel`, replicada aquí para no acoplar
 * dos áreas).
 */
export function useAdminOrgsViewModel() {
  const orgs = ref<AdminOrgDTO[]>([])
  const total = ref(0)
  const offset = ref(0)
  const filtroEstado = ref<FiltroEstado>('todas')
  const counts = ref<AdminOrgCountsDTO>(COUNTS_VACIOS)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // acción en curso sobre una org concreta (deshabilita su fila)
  const actionLoadingId = ref<string | null>(null)
  const actionError = ref<string | null>(null)

  // detalle abierto en el drawer
  const selectedOrg = ref<AdminOrgDTO | null>(null)
  const selectedOrgDocuments = ref<AdminDocumentDTO[]>([])
  const isLoadingDocuments = ref(false)

  /** Conteo por estado (para las pestañas), independiente de la página actual. */
  const conteosPorEstado = computed<Record<string, number>>(() => counts.value)

  const currentPage = computed(() => Math.floor(offset.value / PAGE_SIZE) + 1)
  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))
  const hasNextPage = computed(() => offset.value + PAGE_SIZE < total.value)
  const hasPrevPage = computed(() => offset.value > 0)

  /** Etiqueta legible en español del estado de verificación. */
  function labelEstado(estado: OrgEstado): string {
    const labels: Record<OrgEstado, string> = {
      pendiente: 'Pendiente',
      activa: 'Activa',
      rechazada: 'Rechazada',
      inactiva: 'Inactiva'
    }
    return labels[estado]
  }

  /** Clases del badge de estado (color según verificación). */
  function colorEstado(estado: OrgEstado): string {
    const colors: Record<OrgEstado, string> = {
      activa: 'bg-green-100 text-green-700',
      pendiente: 'bg-amber-100 text-amber-700',
      rechazada: 'bg-red-100 text-red-700',
      inactiva: 'bg-slate-100 text-slate-500'
    }
    return colors[estado]
  }

  /** Etiqueta legible en español de la función de la organización. */
  function labelTipo(tipo: OrgType): string {
    const labels: Record<OrgType, string> = {
      centro_acopio: 'Centro de acopio',
      punto_distribucion: 'Punto de distribución',
      ambos: 'Acopio y distribución'
    }
    return labels[tipo]
  }

  /** Carga la página actual (según `filtroEstado`/`offset`) y los conteos. */
  async function loadOrgs(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [pagina, nuevosCounts] = await Promise.all([
        adminOrgsService.getOrgs({
          estado: filtroEstado.value,
          limit: PAGE_SIZE,
          offset: offset.value
        }),
        adminOrgsService.getOrgCounts()
      ])
      orgs.value = pagina.items
      total.value = pagina.total
      counts.value = nuevosCounts
      // Página vacía tras una acción (ej. se movió el último item de la página
      // a otro estado): retroceder una página en vez de mostrar un vacío falso.
      if (orgs.value.length === 0 && offset.value > 0 && total.value > 0) {
        offset.value = Math.max(0, offset.value - PAGE_SIZE)
        await loadOrgs()
      }
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudieron cargar las organizaciones.'
    } finally {
      isLoading.value = false
    }
  }

  /** Cambia el filtro de estado activo y vuelve a la primera página. */
  function setFiltro(estado: FiltroEstado): void {
    if (filtroEstado.value === estado) return
    filtroEstado.value = estado
    offset.value = 0
    loadOrgs()
  }

  /** Avanza a la página siguiente, si existe. */
  function nextPage(): void {
    if (!hasNextPage.value) return
    offset.value += PAGE_SIZE
    loadOrgs()
  }

  /** Retrocede a la página anterior, si existe. */
  function prevPage(): void {
    if (!hasPrevPage.value) return
    offset.value = Math.max(0, offset.value - PAGE_SIZE)
    loadOrgs()
  }

  /** Abre el detalle de una organización en el drawer y carga sus documentos. */
  async function selectOrg(org: AdminOrgDTO): Promise<void> {
    selectedOrg.value = org
    selectedOrgDocuments.value = []
    isLoadingDocuments.value = true
    try {
      selectedOrgDocuments.value = await adminOrgsService.getOrgDocuments(org.id)
    } catch {
      // Si falla, el drawer simplemente no muestra documentos.
    } finally {
      isLoadingDocuments.value = false
    }
  }

  /** Cierra el detalle. */
  function clearSelection(): void {
    selectedOrg.value = null
    selectedOrgDocuments.value = []
  }

  /**
   * Ejecuta una acción de moderación sobre una org y recarga la página actual.
   * Centraliza el manejo de `actionLoadingId`, errores y la sincronización del
   * detalle abierto. `nextEstado` es el estado esperado tras la acción: la org
   * puede salir de la página filtrada actual (server-side), así que el detalle
   * abierto se actualiza in-place en vez de buscarla en `orgs.value`.
   */
  async function runAction(
    id: string,
    action: (id: string) => Promise<{ success: boolean; error?: string }>,
    nextEstado: OrgEstado
  ): Promise<void> {
    if (actionLoadingId.value) return
    actionLoadingId.value = id
    actionError.value = null
    try {
      const result = await action(id)
      if (result.success) {
        if (selectedOrg.value?.id === id) {
          selectedOrg.value = { ...selectedOrg.value, estado: nextEstado }
        }
        await loadOrgs()
      } else {
        actionError.value = result.error ?? 'No se pudo completar la acción.'
      }
    } catch (e) {
      actionError.value =
        e instanceof Error ? e.message : 'No se pudo completar la acción.'
    } finally {
      actionLoadingId.value = null
    }
  }

  /** Aprueba una organización pendiente. */
  function approveOrg(id: string): Promise<void> {
    return runAction(id, adminOrgsService.approveOrg, 'activa')
  }

  /** Rechaza una organización pendiente. */
  function rejectOrg(id: string): Promise<void> {
    return runAction(id, adminOrgsService.rejectOrg, 'rechazada')
  }

  /** Desactiva una organización activa. */
  function deactivateOrg(id: string): Promise<void> {
    return runAction(id, adminOrgsService.deactivateOrg, 'inactiva')
  }

  /** Reactiva una organización inactiva. */
  function reactivateOrg(id: string): Promise<void> {
    return runAction(id, adminOrgsService.reactivateOrg, 'activa')
  }

  return {
    // estado
    orgs,
    total,
    filtroEstado,
    isLoading,
    error,
    actionLoadingId,
    actionError,
    selectedOrg,
    selectedOrgDocuments,
    isLoadingDocuments,
    // derivados
    conteosPorEstado,
    currentPage,
    totalPages,
    hasNextPage,
    hasPrevPage,
    labelEstado,
    colorEstado,
    labelTipo,
    // acciones
    loadOrgs,
    setFiltro,
    nextPage,
    prevPage,
    selectOrg,
    clearSelection,
    approveOrg,
    rejectOrg,
    deactivateOrg,
    reactivateOrg
  }
}
