<script setup lang="ts">
import { computed } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import OrgCenterForm from '~/components/org/OrgCenterForm.vue'
import type {
  ActiveEmergencyOption,
  CreateCenterInput,
  GeocodeResult,
  OrgCenterDTO,
  OrgCenterEmergencia,
  NeedDTO
} from '~/services/orgDashboardService'

/**
 * VIEW — Panel de la organización receptora. Puramente visual: recibe todo por
 * props (estado ya derivado por el ViewModel) y comunica intenciones por eventos.
 * No conoce servicios ni composables; el mapeo color/estado y los anchos de barra
 * son lógica de presentación. La confirmación de recepciones (CU-07) vive en su
 * propia pantalla (`/org/receptions`); aquí solo se ofrece un acceso directo.
 */
const props = defineProps<{
  center: OrgCenterDTO | null
  activeNeeds: NeedDTO[]
  urgentNeedsCount: number
  hasCenter: boolean
  coberturaColor: 'critico' | 'warning' | 'ok'
  isLoading: boolean
  error: string | null
  // Formulario del centro (crear cuando no hay centro / editar el existente)
  centerFormDefaults: {
    nombre: string
    direccion: string
    zona: string
    horarioAtencion: string
    latitud: number | null
    longitud: number | null
    emergencia: OrgCenterEmergencia | null
  }
  activeEmergencies: ActiveEmergencyOption[]
  showCenterForm: boolean
  centerFormMode: 'create' | 'edit'
  isSavingCenter: boolean
  centerFormError: string | null
  // Geocodificador (prop-función del ViewModel) para el selector de mapa del form.
  geocode: (query: string) => Promise<GeocodeResult | null>
}>()

const emit = defineEmits<{
  'manage-needs': []
  'go-receptions': []
  'open-center-form': []
  'open-edit-center-form': []
  'close-center-form': []
  'submit-center': [data: CreateCenterInput]
}>()

/** Badge del estado del centro (header). */
const ESTADO_BADGE: Record<OrgCenterDTO['estado'], string> = {
  critico: 'bg-red-100 text-red-700',
  en_capacidad: 'bg-amber-100 text-amber-700',
  cerrado: 'bg-slate-100 text-slate-500'
}
const ESTADO_LABEL: Record<OrgCenterDTO['estado'], string> = {
  critico: 'Crítico',
  en_capacidad: 'En capacidad',
  cerrado: 'Cerrado'
}

/** Color del texto del porcentaje de cobertura según el semáforo. */
const coberturaTextClass = computed(
  () =>
    ({
      critico: 'text-red-600',
      warning: 'text-amber-600',
      ok: 'text-green-600'
    })[props.coberturaColor]
)

/** Color del relleno de la barra de cobertura general. */
const coberturaBarClass = computed(
  () =>
    ({
      critico: 'bg-red-500',
      warning: 'bg-amber-500',
      ok: 'bg-green-500'
    })[props.coberturaColor]
)

/** Color del relleno de la barra de una necesidad según su cobertura. */
function needBarClass(cobertura: number): string {
  if (cobertura < 30) return 'bg-red-400'
  if (cobertura < 70) return 'bg-amber-400'
  return 'bg-green-400'
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-6">
    <!-- Estado error -->
    <p
      v-if="error"
      role="alert"
      class="rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
    >
      {{ error }}
    </p>

    <!-- Estado loading inicial: skeleton -->
    <div v-else-if="isLoading" class="flex flex-col gap-6">
      <div class="h-16 animate-pulse rounded-2xl bg-slate-200" />
      <div class="h-40 animate-pulse rounded-2xl bg-slate-200" />
      <div class="h-40 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <!-- Estado "sin centro": la org existe pero aún no tiene centro asignado -->
    <div
      v-else-if="!hasCenter"
      class="glass-auth rounded-2xl px-4 py-12 text-center"
    >
      <h1 class="font-display text-xl font-black uppercase text-navy-800">
        Aún no tienes un centro registrado
      </h1>
      <p class="mt-2 text-sm text-slate-500">
        Crea tu centro de acopio para empezar a publicar necesidades y recibir
        donaciones. Verás aquí su cobertura, sus necesidades y las recepciones
        pendientes.
      </p>
      <div class="mt-5 flex justify-center">
        <BaseButton variant="navy" size="md" @click="emit('open-center-form')">
          Crear centro
        </BaseButton>
      </div>
    </div>

    <!-- Contenido -->
    <div v-else-if="center" class="flex flex-col gap-6">
      <!-- ===== BLOQUE 1: HEADER ===== -->
      <header class="flex flex-wrap items-start justify-between gap-3">
        <div class="min-w-0">
          <h1 class="font-display text-2xl font-black uppercase leading-tight text-navy-800">
            {{ center.nombre }}
          </h1>
          <p class="mt-0.5 text-sm text-slate-500">
            {{ center.zona }} · {{ center.direccion }}
          </p>
          <!-- Emergencia a la que responde el centro (badge) -->
          <span
            v-if="center.emergencia"
            class="mt-2 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
            :class="center.emergencia.estado === 'activa'
              ? 'bg-navy-800/8 text-navy-800'
              : 'bg-slate-100 text-slate-500'"
          >
            <svg
              class="h-3.5 w-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <path d="M12 9v4" />
              <path d="M12 17h.01" />
            </svg>
            Responde a: {{ center.emergencia.nombre }}
            <span v-if="center.emergencia.estado === 'cerrada'" class="text-slate-400">(cerrada)</span>
          </span>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <span
            class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
            :class="ESTADO_BADGE[center.estado]"
          >
            {{ ESTADO_LABEL[center.estado] }}
          </span>
          <button
            type="button"
            class="rounded-lg border border-navy-600/25 px-3 py-1.5 text-xs font-semibold
                   text-navy-600 transition-colors hover:bg-navy-800/8 hover:text-navy-800"
            @click="emit('open-edit-center-form')"
          >
            Editar centro
          </button>
        </div>
      </header>

      <!-- ===== BLOQUE 2: COBERTURA GENERAL ===== -->
      <!--
        TODO(distribución): el panel "Distribución de insumos" (recibido /
        distribuido / enviado a terreno / entregado) se retiró porque NO forma
        parte de GET /org/center. Reintroducir cuando exista un endpoint de
        distribución (p. ej. GET /org/distribution); hoy esos datos solo existen
        como mock en distributionService para la pantalla /org/distribution.
      -->
      <section class="glass-auth rounded-2xl p-5">
        <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Cobertura general
        </h2>
        <p class="mt-2 font-display text-5xl font-black" :class="coberturaTextClass">
          {{ center.totales.coberturaGeneral }}%
        </p>
        <div class="mt-3 h-4 w-full overflow-hidden rounded-full bg-slate-200">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="coberturaBarClass"
            :style="{ width: `${Math.min(100, Math.max(0, center.totales.coberturaGeneral))}%` }"
          />
        </div>
        <p class="mt-2 text-sm text-slate-500">
          {{ activeNeeds.length }}
          {{ activeNeeds.length === 1 ? 'activa' : 'activas' }}
          · {{ urgentNeedsCount }}
          {{ urgentNeedsCount === 1 ? 'urgente' : 'urgentes' }}
        </p>
      </section>

      <!-- ===== BLOQUE 3: RECEPCIONES (acceso directo) ===== -->
      <section class="glass-auth rounded-2xl p-5">
        <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Recepciones
        </h2>
        <p class="mt-2 text-sm text-slate-500">
          Confirma las donaciones que llegan a tu centro ingresando su código de
          seguimiento.
        </p>
        <BaseButton
          variant="navy"
          class="mt-4"
          @click="emit('go-receptions')"
        >
          Confirmar recepciones →
        </BaseButton>
      </section>

      <!-- ===== BLOQUE 4: NECESIDADES ACTIVAS ===== -->
      <section class="glass-auth rounded-2xl p-5">
        <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Necesidades activas
        </h2>

        <p v-if="activeNeeds.length === 0" class="mt-4 text-sm text-slate-400">
          No hay necesidades activas publicadas
        </p>

        <ul v-else class="mt-4 flex flex-col divide-y divide-slate-100">
          <li v-for="need in activeNeeds" :key="need.id" class="py-3 first:pt-0">
            <div class="flex items-center gap-2">
              <span
                v-if="need.urgencia === 'alta'"
                class="alert-pulse h-2 w-2 shrink-0 rounded-full bg-alert"
                aria-hidden="true"
              />
              <span class="min-w-0 flex-1 truncate text-sm font-medium text-navy-800">
                {{ need.insumo.nombre }}
              </span>
              <span class="shrink-0 text-xs text-slate-500">
                {{ need.cantidadComprometida }} / {{ need.cantidadRequerida }} {{ need.insumo.unidad }}
              </span>
            </div>
            <p class="mt-0.5 text-xs text-slate-400">
              {{ need.insumo.categoria }}
            </p>
            <div class="mt-1.5 h-1.5 w-full overflow-hidden rounded bg-slate-200">
              <div
                class="h-full rounded transition-all duration-500"
                :class="needBarClass(need.cobertura)"
                :style="{ width: `${Math.min(100, Math.max(0, need.cobertura))}%` }"
              />
            </div>
          </li>
        </ul>

        <BaseButton
          variant="ghost"
          class="mt-4"
          @click="emit('manage-needs')"
        >
          Gestionar necesidades →
        </BaseButton>
      </section>
    </div>

    <!-- Modal del centro: crear (estado "sin centro") o editar el existente -->
    <OrgCenterForm
      :is-open="showCenterForm"
      :mode="centerFormMode"
      :defaults="centerFormDefaults"
      :emergencies="activeEmergencies"
      :submit-error="centerFormError"
      :is-submitting="isSavingCenter"
      :geocode="geocode"
      @close="emit('close-center-form')"
      @submit="(data) => emit('submit-center', data)"
    />
  </div>
</template>
