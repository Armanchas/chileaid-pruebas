import { computed, ref } from 'vue'
import {
  adminEmergenciesService,
  type CreateEmergencyInput,
  type EmergencyDTO,
  type EmergencyStatus
} from '~/services/adminEmergenciesService'

/** Filtro por estado: `todas` es el valor neutro que no filtra. */
type EstadoFiltro = 'todas' | EmergencyStatus

/**
 * VIEW-MODEL — Puente reactivo de la gestión de emergencias del administrador
 * (`/admin/emergencies`).
 *
 * Es el ÚNICO punto que habla con `adminEmergenciesService`. Carga el listado
 * (activas + cerradas), mantiene el filtro por estado y orquesta el alta y el
 * cierre. Las vistas solo consumen estado/derivados por props y emiten intenciones.
 */
export function useAdminEmergenciesViewModel() {
  const emergencies = ref<EmergencyDTO[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Modal de alta
  const showCreateModal = ref<boolean>(false)
  const submitError = ref<string | null>(null)
  const isSubmitting = ref<boolean>(false)

  // Cierre en curso (deshabilita la fila mientras corre)
  const closingId = ref<string | null>(null)

  // Filtro por estado
  const selectedEstado = ref<EstadoFiltro>('todas')

  /** Emergencias filtradas por estado. */
  const emergenciesFiltradas = computed<EmergencyDTO[]>(() => {
    if (selectedEstado.value === 'todas') return emergencies.value
    return emergencies.value.filter((e) => e.estado === selectedEstado.value)
  })

  /** Conteo por estado + entrada `todas` con el total. */
  const estadoCounts = computed<Record<string, number>>(() => {
    const counts: Record<string, number> = {
      todas: emergencies.value.length,
      activa: 0,
      cerrada: 0
    }
    for (const em of emergencies.value) {
      counts[em.estado] = (counts[em.estado] ?? 0) + 1
    }
    return counts
  })

  /** Carga el listado completo (activas + cerradas). */
  async function loadEmergencies(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      emergencies.value = await adminEmergenciesService.getEmergencies()
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudieron cargar las emergencias.'
    } finally {
      isLoading.value = false
    }
  }

  /** Abre el modal de alta (limpia errores previos del formulario). */
  function openCreateModal(): void {
    submitError.value = null
    showCreateModal.value = true
  }

  /** Cierra el modal de alta. */
  function closeCreateModal(): void {
    showCreateModal.value = false
  }

  /**
   * Crea una emergencia. En éxito recarga el listado y cierra el modal; en error
   * (validación) expone el mensaje del service.
   */
  async function submitCreate(input: CreateEmergencyInput): Promise<void> {
    if (isSubmitting.value) return
    isSubmitting.value = true
    submitError.value = null
    try {
      await adminEmergenciesService.createEmergency(input)
      await loadEmergencies()
      showCreateModal.value = false
    } catch (e) {
      submitError.value =
        e instanceof Error ? e.message : 'No se pudo crear la emergencia.'
    } finally {
      isSubmitting.value = false
    }
  }

  /**
   * Cierra una emergencia y reemplaza el ítem en el estado con el DTO devuelto
   * (sin recargar todo). Un 404/409 se muestra en `error`.
   */
  async function closeEmergency(id: string): Promise<void> {
    if (closingId.value) return
    closingId.value = id
    error.value = null
    try {
      const result = await adminEmergenciesService.closeEmergency(id)
      if (result.success && result.emergency) {
        const idx = emergencies.value.findIndex((e) => e.id === id)
        if (idx !== -1) emergencies.value[idx] = result.emergency
      } else {
        error.value = result.error ?? 'No se pudo cerrar la emergencia.'
      }
    } finally {
      closingId.value = null
    }
  }

  /** Cambia el estado seleccionado del filtro. */
  function setEstado(e: EstadoFiltro): void {
    selectedEstado.value = e
  }

  return {
    // estado
    emergencies,
    isLoading,
    error,
    showCreateModal,
    submitError,
    isSubmitting,
    closingId,
    selectedEstado,
    // derivados
    emergenciesFiltradas,
    estadoCounts,
    // acciones
    loadEmergencies,
    openCreateModal,
    closeCreateModal,
    submitCreate,
    closeEmergency,
    setEstado
  }
}
