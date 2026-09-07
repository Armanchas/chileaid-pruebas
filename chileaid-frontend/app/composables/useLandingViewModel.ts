import { computed, ref } from 'vue'
import {
  statsService,
  type EmergencyNumber,
  type HeroContent,
  type StatItem,
  type TutorialTrack
} from '~/services/statsService'

/**
 * VIEW-MODEL — Puente reactivo entre la vista y el modelo.
 *
 * Es el ÚNICO punto de la app que habla con `statsService`. Expone estado
 * reactivo (ref/computed) y métodos; los componentes nunca tocan el servicio,
 * solo consumen lo que aquí se publica (vía props desde la página).
 */
export function useLandingViewModel() {
  const hero = ref<HeroContent | null>(null)
  const stats = ref<StatItem[]>([])
  const tutorial = ref<TutorialTrack[]>([])
  const emergencyNumbers = ref<EmergencyNumber[]>([])

  /**
   * Imágenes de fondo del hero (carrusel). Fotografías reales de rescate,
   * voluntariado y ayuda humanitaria. Se exponen como dato del ViewModel para
   * que la vista (HeroCarousel) las consuma solo vía props.
   */
  const heroImages = ref<string[]>([
    'https://images.unsplash.com/photo-1615092296061-e2ccfeb2f3d6?auto=format&fit=crop&w=1920&q=80',
    'https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?auto=format&fit=crop&w=1920&q=80',
    'https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1920&q=80'
  ])

  const isLoading = ref(false)
  const error = ref<string | null>(null)

  /** Indica si ya hay estadísticas listas para animar su entrada. */
  const hasStats = computed(() => stats.value.length > 0)

  /** Carga toda la data necesaria para la landing en paralelo. */
  async function loadLanding(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [heroData, statsData, tutorialData, emergencyData] = await Promise.all([
        statsService.getHeroContent(),
        statsService.getStats(),
        statsService.getTutorial(),
        statsService.getEmergencyNumbers()
      ])
      hero.value = heroData
      stats.value = statsData
      tutorial.value = tutorialData
      emergencyNumbers.value = emergencyData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'No se pudo cargar la información.'
    } finally {
      isLoading.value = false
    }
  }

  // --- Intenciones de la vista (placeholder hasta tener rutas/API) ---

  function onDonate(): void {
    navigateTo('/register/donor')
  }

  function onRegisterCenter(): void {
    navigateTo('/register/org')
  }

  /** Abre el mapa público de centros (sin exigir sesión). */
  function onViewMap(): void {
    navigateTo('/map')
  }

  return {
    // estado
    hero,
    heroImages,
    stats,
    tutorial,
    emergencyNumbers,
    isLoading,
    error,
    hasStats,
    // acciones
    loadLanding,
    onDonate,
    onRegisterCenter,
    onViewMap
  }
}
