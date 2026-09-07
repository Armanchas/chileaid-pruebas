import { computed, ref } from 'vue'
import {
  orgNeedsService,
  type InsumoCatalogDTO,
  type CreateNeedInput,
  type UpdateNeedInput
} from '~/services/orgNeedsService'
import type { NeedDTO } from '~/services/orgDashboardService'

/**
 * VIEW-MODEL — Puente reactivo entre la gestión de necesidades de la organización
 * y el modelo.
 *
 * Es el ÚNICO punto de la app que habla con `orgNeedsService`. Expone estado
 * reactivo (ref) y las intenciones (`loadData`, abrir/cerrar el modal,
 * `submitForm`, `closeNeed`); los componentes nunca tocan el servicio, solo
 * consumen lo que aquí se publica vía props desde la página.
 *
 * El mismo modal sirve para crear y editar: `selectedNeed === null` es alta (se
 * elige el insumo del catálogo); `selectedNeed !== null` es edición (el insumo
 * queda bloqueado, solo se ajustan cantidad y urgencia).
 */
export function useOrgNeedsViewModel() {
  const needs = ref<NeedDTO[]>([])
  const catalog = ref<InsumoCatalogDTO[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Modal de formulario (crear / editar) y feedback de escritura
  const showFormModal = ref<boolean>(false)
  const selectedNeed = ref<NeedDTO | null>(null)
  const isSubmitting = ref<boolean>(false)
  const submitError = ref<string | null>(null)

  // Cierre manual de una necesidad (CU-03). `closingId` = id en curso.
  const closingId = ref<string | null>(null)

  /** `true` cuando el modal está en modo edición (hay una necesidad seleccionada). */
  const isEditing = computed<boolean>(() => selectedNeed.value !== null)

  /**
   * Carga en paralelo las necesidades activas y el catálogo de insumos. Maneja
   * los estados de carga y error de forma centralizada.
   */
  async function loadData(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [needsData, catalogData] = await Promise.all([
        orgNeedsService.getOrgNeeds(),
        orgNeedsService.getInsumosCatalog()
      ])
      needs.value = needsData
      catalog.value = catalogData
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudieron cargar las necesidades.'
    } finally {
      isLoading.value = false
    }
  }

  /** Abre el modal en modo alta (sin necesidad seleccionada). */
  function openCreateModal(): void {
    submitError.value = null
    selectedNeed.value = null
    showFormModal.value = true
  }

  /** Abre el modal en modo edición, precargado con la necesidad recibida. */
  function openEditModal(need: NeedDTO): void {
    submitError.value = null
    selectedNeed.value = need
    showFormModal.value = true
  }

  /** Cierra el modal de formulario y limpia la selección. */
  function closeFormModal(): void {
    showFormModal.value = false
    selectedNeed.value = null
  }

  /**
   * Publica una nueva necesidad. En éxito cierra el modal y refresca los datos;
   * en error expone el mensaje sin cerrar el modal.
   */
  async function submitCreate(data: CreateNeedInput): Promise<void> {
    if (isSubmitting.value) return

    isSubmitting.value = true
    submitError.value = null
    try {
      await orgNeedsService.createOrgNeed(data)
      closeFormModal()
      await loadData()
    } catch (e) {
      submitError.value =
        e instanceof Error ? e.message : 'No se pudo publicar la necesidad.'
    } finally {
      isSubmitting.value = false
    }
  }

  /**
   * Actualiza cantidad y urgencia de una necesidad existente. En éxito cierra el
   * modal y refresca los datos; en error expone el mensaje sin cerrar el modal.
   */
  async function submitUpdate(id: string, data: UpdateNeedInput): Promise<void> {
    if (isSubmitting.value) return

    isSubmitting.value = true
    submitError.value = null
    try {
      await orgNeedsService.updateOrgNeed(id, data)
      closeFormModal()
      await loadData()
    } catch (e) {
      submitError.value =
        e instanceof Error ? e.message : 'No se pudo actualizar la necesidad.'
    } finally {
      isSubmitting.value = false
    }
  }

  /**
   * Punto de entrada único del modal: enruta hacia alta o edición según haya o no
   * una necesidad seleccionada. En edición ignora el insumo (no se puede cambiar)
   * y solo envía cantidad y urgencia. Mantiene la página libre de lógica.
   */
  async function submitForm(data: CreateNeedInput): Promise<void> {
    if (selectedNeed.value) {
      await submitUpdate(selectedNeed.value.id, {
        cantidadRequerida: data.cantidadRequerida,
        urgencia: data.urgencia
      })
    } else {
      await submitCreate(data)
    }
  }

  /**
   * Cierre manual de una necesidad (`PATCH /org/needs/{id}/cerrar`). En éxito
   * reemplaza el item en el estado local con el `NeedDTO` devuelto (queda
   * `estado='cerrada'`), sin recargar toda la lista. `closingId` permite a la
   * vista atenuar/deshabilitar la tarjeta en curso.
   */
  async function closeNeed(id: string): Promise<void> {
    if (closingId.value) return

    closingId.value = id
    error.value = null
    try {
      const updated = await orgNeedsService.closeOrgNeed(id)
      const i = needs.value.findIndex((n) => n.id === id)
      if (i !== -1) needs.value[i] = updated
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudo cerrar la necesidad.'
    } finally {
      closingId.value = null
    }
  }

  return {
    // estado
    needs,
    catalog,
    isLoading,
    error,
    showFormModal,
    selectedNeed,
    isEditing,
    isSubmitting,
    submitError,
    closingId,
    // acciones
    loadData,
    openCreateModal,
    openEditModal,
    closeFormModal,
    submitCreate,
    submitUpdate,
    submitForm,
    closeNeed
  }
}
