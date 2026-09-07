/**
 * MODEL — Capa de acceso a datos del landing público.
 *
 * Conectado al backend real vía `apiFetch` (endpoints públicos, sin token):
 *   getStats            → `GET /stats`                    (4 métricas agregadas)
 *   getHeroContent      → `GET /content/hero`
 *   getHowItWorks       → `GET /content/how-it-works`
 *   getEmergencyNumbers → `GET /content/emergency-numbers`
 *
 * El backend devuelve el `value` crudo + `label`; el `display` ("45K+") lo formatea
 * este service (presentación), única adaptación del contrato.
 */
import { apiFetch } from '~/utils/apiFetch'

export interface StatItem {
  /** Identificador estable para keys de render */
  id: string
  /** Valor numérico crudo (para animaciones / cálculos futuros) */
  value: number
  /** Valor ya formateado para mostrar: "142", "45K+", "12K+" */
  display: string
  /** Etiqueta descriptiva bajo el número */
  label: string
}

export interface HeroContent {
  badge: string
  title: string
  subtitle: string
  primaryCta: string
  secondaryCta: string
}

export interface HowItWorksCard {
  id: string
  audience: string
  title: string
  description: string
  steps: string[]
  cta: string
  accent: 'navy' | 'alert'
}

export interface EmergencyNumber {
  id: string
  name: string
  number: string
}

/** Un paso del tutorial. `icon` es una clave que la vista resuelve a un SVG. */
export interface TutorialStep {
  icon: string
  title: string
  description: string
}

/** Un carril del tutorial ("cómo donar" / "cómo solicitar"). */
export interface TutorialTrack {
  id: string
  audience: string
  title: string
  steps: TutorialStep[]
  cta: string
  accent: 'navy' | 'alert'
}

/** Forma cruda de una métrica del backend (`StatItemDTO`): sin `display`. */
interface ApiStatItem {
  id: string
  value: number
  label: string
}

/** Formatea el valor para mostrar: 45000 → "45K+", 142 → "142". */
function formatDisplay(value: number): string {
  if (value >= 1000) return `${Math.floor(value / 1000)}K+`
  return String(value)
}

export const statsService = {
  /** Métricas agregadas de la operación nacional (`GET /stats`). */
  async getStats(): Promise<StatItem[]> {
    const api = await apiFetch<ApiStatItem[]>('/stats')
    return api.map((s) => ({ ...s, display: formatDisplay(s.value) }))
  },

  /** Contenido del hero principal (`GET /content/hero`). */
  async getHeroContent(): Promise<HeroContent> {
    return apiFetch<HeroContent>('/content/hero')
  },

  /** Tarjetas de la sección "Cómo funciona" (`GET /content/how-it-works`). */
  async getHowItWorks(): Promise<HowItWorksCard[]> {
    return apiFetch<HowItWorksCard[]>('/content/how-it-works')
  },

  /** Tutorial visual "cómo donar / cómo solicitar" (`GET /content/tutorial`). */
  async getTutorial(): Promise<TutorialTrack[]> {
    return apiFetch<TutorialTrack[]>('/content/tutorial')
  },

  /** Números de emergencia oficiales de Chile (`GET /content/emergency-numbers`). */
  async getEmergencyNumbers(): Promise<EmergencyNumber[]> {
    return apiFetch<EmergencyNumber[]>('/content/emergency-numbers')
  }
}
