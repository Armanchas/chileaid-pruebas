import { computed, ref } from 'vue'
import {
  orgReceptionsService,
  type PendingReceptionDTO
} from '~/services/orgReceptionsService'

/**
 * VIEW-MODEL — Puente reactivo de la confirmación de recepciones (CU-07,
 * `/org/receptions`).
 *
 * Es el ÚNICO punto que habla con `orgReceptionsService`. Carga las donaciones
 * pendientes del centro de la org y confirma una por su código (manual; el
 * escáner QR queda fuera de alcance). Tras confirmar, recarga la lista para que
 * la donación recién confirmada desaparezca. Los componentes solo consumen lo que
 * aquí se publica por props y emiten intenciones.
 */
export function useOrgReceptionsViewModel() {
  const pendingReceptions = ref<PendingReceptionDTO[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Confirmación por código manual
  const receptionCode = ref<string>('')
  const isConfirming = ref<boolean>(false)
  const confirmError = ref<string | null>(null)
  const confirmSuccess = ref<string | null>(null)

  /** Verdadero si hay al menos una recepción pendiente de confirmar. */
  const hasPendingReceptions = computed<boolean>(
    () => pendingReceptions.value.length > 0
  )

  /** Carga las recepciones pendientes del centro de la org autenticada. */
  async function loadReceptions(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      pendingReceptions.value = await orgReceptionsService.getPendingReceptions()
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudieron cargar las recepciones.'
    } finally {
      isLoading.value = false
    }
  }

  /** Actualiza el código tecleado y limpia el feedback previo. */
  function setReceptionCode(code: string): void {
    receptionCode.value = code
    if (confirmError.value || confirmSuccess.value) {
      confirmError.value = null
      confirmSuccess.value = null
    }
  }

  /**
   * Confirma la recepción del código dado (o el del campo). En éxito limpia el
   * campo, muestra el feedback y recarga la lista de pendientes; en error expone
   * el mensaje del backend (404/403/409).
   */
  async function confirmReception(codigo?: string): Promise<void> {
    if (isConfirming.value) return
    const code = (codigo ?? receptionCode.value).trim()

    isConfirming.value = true
    confirmError.value = null
    confirmSuccess.value = null
    try {
      const result = await orgReceptionsService.confirmReception(code)
      if (result.success) {
        confirmSuccess.value = `Recepción ${code} confirmada`
        receptionCode.value = ''
        await loadReceptions()
      } else {
        confirmError.value = result.error ?? 'No se pudo confirmar la recepción.'
      }
    } catch (e) {
      confirmError.value =
        e instanceof Error ? e.message : 'No se pudo confirmar la recepción.'
    } finally {
      isConfirming.value = false
    }
  }

  /** Vuelve al panel de la organización. */
  function goBack(): void {
    navigateTo('/org')
  }

  return {
    // estado
    pendingReceptions,
    isLoading,
    error,
    receptionCode,
    isConfirming,
    confirmError,
    confirmSuccess,
    // derivados
    hasPendingReceptions,
    // acciones
    loadReceptions,
    setReceptionCode,
    confirmReception,
    goBack
  }
}
