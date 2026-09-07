import { computed, ref } from 'vue'
import {
  adminCatalogService,
  type InsumoCatalogDTO,
  type CreateInsumoInput
} from '~/services/adminCatalogService'

/**
 * VIEW-MODEL — Puente reactivo de la gestión del catálogo de insumos del
 * administrador (`/admin/catalog`).
 *
 * Es el ÚNICO punto que habla con `adminCatalogService`. Carga el catálogo,
 * mantiene los filtros (búsqueda + categoría) y orquesta el alta/baja de insumos.
 * Las vistas solo consumen estado/derivados por props y emiten intenciones.
 */
export function useAdminCatalogViewModel() {
  const catalog = ref<InsumoCatalogDTO[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Modal de alta
  const showCreateModal = ref<boolean>(false)
  const submitError = ref<string | null>(null)
  const isSubmitting = ref<boolean>(false)

  // Baja en curso
  const deletingId = ref<string | null>(null)

  // Filtros
  const searchQuery = ref<string>('')
  const selectedCategoria = ref<string>('todas')

  /** Catálogo filtrado por búsqueda (nombre, case-insensitive) y por categoría. */
  const catalogFiltrado = computed<InsumoCatalogDTO[]>(() => {
    const q = searchQuery.value.trim().toLowerCase()
    return catalog.value.filter((i) => {
      const matchSearch = q === '' || i.nombre.toLowerCase().includes(q)
      const matchCategoria =
        selectedCategoria.value === 'todas' || i.categoria === selectedCategoria.value
      return matchSearch && matchCategoria
    })
  })

  /** Conteo por categoría + entrada `todas` con el total. */
  const categoriasCounts = computed<Record<string, number>>(() => {
    const counts: Record<string, number> = { todas: catalog.value.length }
    for (const insumo of catalog.value) {
      counts[insumo.categoria] = (counts[insumo.categoria] ?? 0) + 1
    }
    return counts
  })

  /** Carga el catálogo. Maneja loading y error centralizados. */
  async function loadCatalog(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      catalog.value = await adminCatalogService.getCatalog()
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudo cargar el catálogo.'
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
   * Da de alta un insumo. En éxito recarga el catálogo y cierra el modal; en
   * error (validación o duplicado) expone el mensaje del service.
   */
  async function submitCreate(input: CreateInsumoInput): Promise<void> {
    if (isSubmitting.value) return
    isSubmitting.value = true
    submitError.value = null
    try {
      await adminCatalogService.createInsumo(input)
      await loadCatalog()
      showCreateModal.value = false
    } catch (e) {
      submitError.value =
        e instanceof Error ? e.message : 'No se pudo agregar el insumo.'
    } finally {
      isSubmitting.value = false
    }
  }

  /** Da de baja un insumo y recarga el catálogo. */
  async function deleteInsumo(id: string): Promise<void> {
    if (deletingId.value) return
    deletingId.value = id
    error.value = null
    try {
      const result = await adminCatalogService.deleteInsumo(id)
      if (result.success) {
        await loadCatalog()
      } else {
        // 409 (insumo en uso por needs activas) / 404 → mostrar el error del
        // backend SIN recargar (el insumo sigue en la lista).
        error.value = result.error ?? 'No se pudo eliminar el insumo.'
      }
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudo eliminar el insumo.'
    } finally {
      deletingId.value = null
    }
  }

  /** Actualiza el término de búsqueda. */
  function setSearch(q: string): void {
    searchQuery.value = q
  }

  /** Cambia la categoría seleccionada del filtro. */
  function setCategoria(c: string): void {
    selectedCategoria.value = c
  }

  return {
    // estado
    catalog,
    isLoading,
    error,
    showCreateModal,
    deletingId,
    submitError,
    isSubmitting,
    searchQuery,
    selectedCategoria,
    // derivados
    catalogFiltrado,
    categoriasCounts,
    // acciones
    loadCatalog,
    openCreateModal,
    closeCreateModal,
    submitCreate,
    deleteInsumo,
    setSearch,
    setCategoria
  }
}
