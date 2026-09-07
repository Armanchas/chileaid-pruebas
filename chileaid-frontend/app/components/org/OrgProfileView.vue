<script setup lang="ts">
import { computed } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import OrgDocumentsSection from '~/components/org/OrgDocumentsSection.vue'
import type { OrgProfileDTO, OrgType } from '~/services/orgProfileService'

/**
 * VIEW — Perfil de la organización receptora: identidad fija + datos de contacto
 * editables + estadísticas de actividad. Puramente visual: recibe todo por props
 * y comunica intenciones por eventos. No conoce servicios ni composables. Las
 * iniciales del avatar, el color del badge de tipo y el formato de fecha son
 * presentación derivada.
 */
const props = defineProps<{
  profile: OrgProfileDTO | null
  form: {
    contactoNombre: string
    email: string
    telefono: string
    region: string
  }
  isLoading: boolean
  isSaving: boolean
  error: string | null
  saveError: string | null
  saveSuccess: boolean
  labelTipo: string
  labelEstado: string
  colorEstado: string
  isFormDirty: boolean
  regiones: string[]
}>()

const emit = defineEmits<{
  'update:form': [
    field: 'contactoNombre' | 'email' | 'telefono' | 'region',
    value: string
  ]
  save: []
  reset: []
  'go-back': []
}>()

/** Clases del badge según la función de la organización. */
const TIPO_BADGE: Record<OrgType, string> = {
  centro_acopio: 'bg-blue-100 text-blue-800',
  punto_distribucion: 'bg-teal-100 text-teal-800',
  ambos: 'bg-purple-100 text-purple-700'
}

/** Color del badge de tipo derivado del perfil. */
const colorTipo = computed(() =>
  props.profile ? TIPO_BADGE[props.profile.tipo] : ''
)

/** Iniciales del avatar a partir del nombre de la organización. */
const iniciales = computed(() => {
  if (!props.profile) return ''
  return props.profile.nombre
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word.charAt(0))
    .join('')
    .toUpperCase()
})

/** Fecha de registro formateada legible (ej. "15 de marzo de 2025"). */
const fechaRegistroLegible = computed(() => {
  if (!props.profile) return ''
  const [year, month, day] = props.profile.fechaRegistro.split('-').map(Number)
  if (!year || !month || !day) return props.profile.fechaRegistro
  const fecha = new Date(year, month - 1, day)
  return fecha.toLocaleDateString('es-CL', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
})

/** Reenvía el cambio de un campo del formulario hacia el ViewModel. */
function onFieldInput(
  field: 'contactoNombre' | 'email' | 'telefono' | 'region',
  event: Event
): void {
  emit(
    'update:form',
    field,
    (event.target as HTMLInputElement | HTMLSelectElement).value
  )
}
</script>

<template>
  <div class="min-h-screen bg-[#f0f4ff]">
    <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
      <!-- Header -->
      <header class="mb-6">
        <button
          type="button"
          class="flex items-center gap-1.5 text-sm font-semibold text-navy-600 hover:text-navy-800"
          @click="emit('go-back')"
        >
          <svg
            class="h-4 w-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
          Volver al panel
        </button>
        <h1 class="mt-3 font-display text-3xl font-black uppercase tracking-wide text-navy-800">
          Perfil de la organización
        </h1>
      </header>

      <!-- Estado error general -->
      <p
        v-if="error"
        role="alert"
        class="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-600"
      >
        {{ error }}
      </p>

      <!-- Estado loading: skeletons -->
      <div v-else-if="isLoading || !profile" class="flex flex-col gap-6">
        <div class="h-48 animate-pulse rounded-2xl bg-slate-200" />
        <div class="h-80 animate-pulse rounded-2xl bg-slate-200" />
        <div class="h-32 animate-pulse rounded-2xl bg-slate-200" />
      </div>

      <!-- Contenido -->
      <div v-else class="flex flex-col gap-6">
        <!-- ───────── SECCIÓN 1 — Identidad (no editable) ───────── -->
        <section class="glass-auth rounded-2xl p-5 sm:p-6">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-start">
            <!-- Avatar cuadrado (org) -->
            <span
              class="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-navy-800
                     font-display text-xl font-black uppercase text-white"
              aria-hidden="true"
            >
              {{ iniciales }}
            </span>

            <div class="min-w-0 flex-1">
              <h2 class="font-display text-2xl font-black uppercase text-navy-800">
                {{ profile.nombre }}
              </h2>

              <!-- Badges -->
              <div class="mt-2 flex flex-wrap items-center gap-2">
                <span
                  class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="colorTipo"
                >
                  {{ labelTipo }}
                </span>
                <span
                  class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="colorEstado"
                >
                  {{ labelEstado }}
                </span>
              </div>

              <!-- Datos secundarios -->
              <dl class="mt-4 grid grid-cols-1 gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
                <div class="flex gap-1.5">
                  <dt class="font-semibold text-slate-500">RUT:</dt>
                  <dd class="text-navy-800">{{ profile.rut }}</dd>
                </div>
                <div class="flex gap-1.5">
                  <dt class="font-semibold text-slate-500">Región:</dt>
                  <dd class="text-navy-800">{{ profile.region }}</dd>
                </div>
                <div class="flex gap-1.5">
                  <dt class="font-semibold text-slate-500">Miembro desde:</dt>
                  <dd class="text-navy-800">{{ fechaRegistroLegible }}</dd>
                </div>
                <div class="flex items-center gap-1.5">
                  <dt class="sr-only">Documentación</dt>
                  <svg
                    class="h-4 w-4 shrink-0 text-slate-400"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <path d="M14 2v6h6" />
                  </svg>
                  <dd class="truncate text-slate-500">{{ profile.documentacion }}</dd>
                </div>
              </dl>
            </div>
          </div>

          <!-- Aviso de estado pendiente -->
          <div
            v-if="profile.estado === 'pendiente'"
            class="glass-auth mt-5 rounded-xl border-l-4 border-amber-400 px-4 py-3 text-sm text-navy-800"
          >
            Tu organización está pendiente de verificación. El equipo de Chile Aid
            revisará la documentación enviada.
          </div>

          <!-- Aviso de estado rechazado -->
          <div
            v-else-if="profile.estado === 'rechazada'"
            class="glass-auth mt-5 rounded-xl border-l-4 border-red-400 px-4 py-3 text-sm text-navy-800"
          >
            La solicitud de tu organización fue rechazada. Revisa la documentación
            enviada o contacta al equipo de Chile Aid.
            <p v-if="profile.motivoRechazo" class="mt-1.5 font-semibold">
              Motivo: {{ profile.motivoRechazo }}
            </p>
          </div>
        </section>

        <!-- ───────── SECCIÓN 2 — Datos de contacto (editables) ───────── -->
        <section class="glass-auth rounded-2xl p-5 sm:p-6">
          <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Datos de contacto
          </h2>
          <p class="mt-1 text-sm text-slate-500">
            Estos datos son visibles para los donantes
          </p>

          <div class="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <!-- Nombre del coordinador -->
            <div>
              <label
                for="org-contacto"
                class="block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
              >
                Nombre del coordinador
              </label>
              <input
                id="org-contacto"
                type="text"
                :value="form.contactoNombre"
                placeholder="Nombre y apellido"
                class="mt-1.5 w-full rounded-lg border border-navy-800/15 bg-white px-3 py-2
                       text-navy-900 placeholder:text-slate-400
                       focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20"
                @input="onFieldInput('contactoNombre', $event)"
              >
            </div>

            <!-- Email institucional -->
            <div>
              <label
                for="org-email"
                class="block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
              >
                Email institucional
              </label>
              <input
                id="org-email"
                type="email"
                :value="form.email"
                placeholder="contacto@organizacion.cl"
                class="mt-1.5 w-full rounded-lg border border-navy-800/15 bg-white px-3 py-2
                       text-navy-900 placeholder:text-slate-400
                       focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20"
                @input="onFieldInput('email', $event)"
              >
            </div>

            <!-- Teléfono de contacto -->
            <div>
              <label
                for="org-telefono"
                class="block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
              >
                Teléfono de contacto
              </label>
              <input
                id="org-telefono"
                type="tel"
                :value="form.telefono"
                placeholder="+56 9 1234 5678"
                class="mt-1.5 w-full rounded-lg border border-navy-800/15 bg-white px-3 py-2
                       text-navy-900 placeholder:text-slate-400
                       focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20"
                @input="onFieldInput('telefono', $event)"
              >
            </div>

            <!-- Región -->
            <div>
              <label
                for="org-region"
                class="block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
              >
                Región
              </label>
              <select
                id="org-region"
                :value="form.region"
                class="mt-1.5 w-full rounded-lg border border-navy-800/15 bg-white px-3 py-2
                       text-navy-900
                       focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20"
                @change="onFieldInput('region', $event)"
              >
                <option v-for="region in regiones" :key="region" :value="region">
                  {{ region }}
                </option>
              </select>
            </div>
          </div>

          <!-- Feedback de guardado -->
          <p
            v-if="saveSuccess"
            class="mt-5 rounded-lg bg-green-50 px-4 py-3 text-sm font-semibold text-green-700 ring-1 ring-green-600/30"
          >
            ✓ Cambios guardados correctamente
          </p>
          <p
            v-else-if="saveError"
            class="mt-5 text-sm font-semibold text-red-600"
          >
            {{ saveError }}
          </p>

          <!-- Botones -->
          <div class="mt-5 flex flex-wrap items-center justify-end gap-3">
            <BaseButton
              v-if="isFormDirty"
              variant="ghost"
              @click="emit('reset')"
            >
              Cancelar cambios
            </BaseButton>
            <BaseButton
              variant="navy"
              :disabled="!isFormDirty || isSaving"
              @click="emit('save')"
            >
              {{ isSaving ? 'Guardando…' : 'Guardar cambios' }}
            </BaseButton>
          </div>
        </section>

        <!-- ───────── SECCIÓN 3 — Documentos de respaldo ───────── -->
        <OrgDocumentsSection />

        <!-- ───────── SECCIÓN 4 — Estadísticas de actividad (solo lectura) ───────── -->
        <section class="glass-auth rounded-2xl p-5 sm:p-6">
          <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Actividad de la organización
          </h2>

          <div class="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div class="rounded-xl bg-white/60 px-4 py-5 text-center ring-1 ring-navy-800/10">
              <p class="font-display text-4xl font-black tabular-nums text-navy-800">47</p>
              <p class="mt-1 text-sm text-slate-500">Donaciones confirmadas</p>
            </div>
            <div class="rounded-xl bg-white/60 px-4 py-5 text-center ring-1 ring-navy-800/10">
              <p class="font-display text-4xl font-black tabular-nums text-navy-800">12</p>
              <p class="mt-1 text-sm text-slate-500">Lotes distribuidos</p>
            </div>
            <div class="rounded-xl bg-white/60 px-4 py-5 text-center ring-1 ring-navy-800/10">
              <p class="font-display text-4xl font-black tabular-nums text-navy-800">380</p>
              <p class="mt-1 text-sm text-slate-500">Insumos entregados</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
