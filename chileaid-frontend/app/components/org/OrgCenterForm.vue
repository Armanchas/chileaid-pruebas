<script setup lang="ts">
/**
 * VIEW — Modal de alta/edición del centro de acopio de la organización. Puramente
 * visual: recibe estado por props y comunica intenciones por eventos
 * (`close`, `submit`). El estado del formulario es local a la vista.
 *
 * Pensado para compartirse entre crear y editar (`mode`): hoy solo se usa para
 * crear (POST /org/center). Los valores iniciales llegan por `defaults` (el VM
 * los prefija con datos de la org); las coordenadas son opcionales pero deben ir
 * juntas (ambas o ninguna) y dentro de rango — se valida en cliente para UX y en
 * el backend como fuente de verdad.
 */
import { computed, ref, watch } from 'vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import LocationPicker from '~/components/org/LocationPicker.vue'
import type {
  ActiveEmergencyOption,
  CreateCenterInput,
  GeocodeResult,
  OrgCenterEmergencia
} from '~/services/orgDashboardService'

const props = withDefaults(
  defineProps<{
    isOpen: boolean
    defaults: {
      nombre: string
      direccion: string
      zona: string
      horarioAtencion: string
      latitud: number | null
      longitud: number | null
      emergencia: OrgCenterEmergencia | null
    }
    emergencies: ActiveEmergencyOption[]
    submitError: string | null
    isSubmitting: boolean
    mode?: 'create' | 'edit'
    /**
     * Geocodificador de direcciones (prop-función provista por el ViewModel, RF-05).
     * El form la invoca al pulsar "Ubicar por dirección"; nunca importa el service.
     * Opcional: sin ella, el picker sigue funcionando a mano (click en el mapa).
     */
    geocode?: (query: string) => Promise<GeocodeResult | null>
  }>(),
  { mode: 'create' }
)

const emit = defineEmits<{
  close: []
  submit: [data: CreateCenterInput]
}>()

const nombre = ref<string>('')
const direccion = ref<string>('')
const zona = ref<string>('')
const horarioAtencion = ref<string>('')
const latitud = ref<string>('')
const longitud = ref<string>('')
// '' = sin emergencia (null); si no, el id de la emergencia seleccionada.
const emergencyId = ref<string>('')

/** Rehidrata el formulario con los valores prefijados cada vez que se abre. */
watch(
  () => props.isOpen,
  (open) => {
    if (!open) return
    nombre.value = props.defaults.nombre
    direccion.value = props.defaults.direccion
    zona.value = props.defaults.zona
    horarioAtencion.value = props.defaults.horarioAtencion
    latitud.value = props.defaults.latitud === null ? '' : String(props.defaults.latitud)
    longitud.value = props.defaults.longitud === null ? '' : String(props.defaults.longitud)
    emergencyId.value = props.defaults.emergencia?.id ?? ''
  },
  { immediate: true }
)

/**
 * Opciones del selector de emergencia: las activas + (si el centro ya está
 * vinculado a una que NO está en la lista activa, p. ej. una cerrada = histórico)
 * esa emergencia, para no perder el vínculo al editar otros campos. Reenviar su
 * id no lo re-valida en el backend (el vínculo no cambia).
 */
const emergencyOptions = computed<{ id: string; label: string }[]>(() => {
  const opts = props.emergencies.map((e) => ({ id: e.id, label: e.nombre }))
  const current = props.defaults.emergencia
  if (current && !opts.some((o) => o.id === current.id)) {
    opts.unshift({
      id: current.id,
      label: current.estado === 'cerrada' ? `${current.nombre} (cerrada)` : current.nombre
    })
  }
  return opts
})

const bothEmpty = computed(
  () => latitud.value.trim() === '' && longitud.value.trim() === ''
)
const bothFilled = computed(
  () => latitud.value.trim() !== '' && longitud.value.trim() !== ''
)
/** Una coordenada sin la otra: estado inválido (deben ir juntas). */
const coordsPartial = computed(() => !bothEmpty.value && !bothFilled.value)

const latNum = computed(() => Number(latitud.value))
const lngNum = computed(() => Number(longitud.value))
/** Ambas presentes, numéricas y dentro de rango (-90..90 / -180..180). */
const coordsInRange = computed(
  () =>
    Number.isFinite(latNum.value) &&
    latNum.value >= -90 &&
    latNum.value <= 90 &&
    Number.isFinite(lngNum.value) &&
    lngNum.value >= -180 &&
    lngNum.value <= 180
)
const coordsValid = computed(
  () => bothEmpty.value || (bothFilled.value && coordsInRange.value)
)

/** Mensaje de ayuda para las coordenadas cuando están incompletas o fuera de rango. */
const coordsHint = computed<string | null>(() => {
  if (coordsPartial.value) return 'Ingresa latitud y longitud juntas, o deja ambas vacías.'
  if (bothFilled.value && !coordsInRange.value)
    return 'Coordenadas fuera de rango (latitud -90 a 90, longitud -180 a 180).'
  return null
})

/** `true` cuando los campos obligatorios están completos y las coordenadas son válidas. */
const isValid = computed<boolean>(
  () =>
    nombre.value.trim() !== '' &&
    direccion.value.trim() !== '' &&
    zona.value.trim() !== '' &&
    coordsValid.value
)

const title = computed(() =>
  props.mode === 'edit' ? 'Editar centro de acopio' : 'Crear centro de acopio'
)
const submitLabel = computed(() => {
  if (props.isSubmitting) return props.mode === 'edit' ? 'Guardando…' : 'Creando…'
  return props.mode === 'edit' ? 'Guardar cambios' : 'Crear centro'
})

// --- Selector de ubicación en el mapa (RF-05) ---

/** Coordenada numérica para el picker, o `null` si el campo no es un número válido. */
const pickerLat = computed<number | null>(() =>
  latitud.value.trim() !== '' && Number.isFinite(latNum.value) ? latNum.value : null
)
const pickerLng = computed<number | null>(() =>
  longitud.value.trim() !== '' && Number.isFinite(lngNum.value) ? lngNum.value : null
)

const geocoding = ref<boolean>(false)
const geocodeError = ref<string | null>(null)

/** Refleja en los inputs el punto elegido (click/arrastre) en el mapa. */
function onPickFromMap(point: { latitud: number; longitud: number }): void {
  latitud.value = String(point.latitud)
  longitud.value = String(point.longitud)
  geocodeError.value = null
}

/** `true` si hay dirección y zona para intentar geocodificar. */
const canGeocode = computed(
  () => direccion.value.trim() !== '' && zona.value.trim() !== ''
)

/**
 * Pide al ViewModel geocodificar la dirección tipeada y, si hay resultado, mueve
 * el pin/rellena las coordenadas. Si no encuentra, invita a ubicarlo a mano.
 */
async function onGeocodeAddress(): Promise<void> {
  if (!props.geocode || !canGeocode.value || geocoding.value) return
  geocoding.value = true
  geocodeError.value = null
  try {
    const query = `${direccion.value.trim()}, ${zona.value.trim()}, Chile`
    const hit = await props.geocode(query)
    if (hit) {
      latitud.value = String(hit.latitud)
      longitud.value = String(hit.longitud)
    } else {
      geocodeError.value =
        'No encontramos esa dirección. Ubica el punto haciendo click en el mapa.'
    }
  } finally {
    geocoding.value = false
  }
}

/** Emite el alta/edición solo si es válido y no está enviando. */
function onSubmit(): void {
  if (!isValid.value || props.isSubmitting) return
  emit('submit', {
    nombre: nombre.value.trim(),
    direccion: direccion.value.trim(),
    zona: zona.value.trim(),
    horarioAtencion: horarioAtencion.value.trim() || null,
    latitud: bothFilled.value ? latNum.value : null,
    longitud: bothFilled.value ? lngNum.value : null,
    emergencyId: emergencyId.value === '' ? null : emergencyId.value
  })
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
    @click.self="emit('close')"
  >
    <div class="glass-auth max-h-[90vh] w-full max-w-md overflow-y-auto rounded-2xl p-6">
      <!-- Header -->
      <div class="flex items-center justify-between gap-3">
        <h2 class="font-display text-lg font-black uppercase text-navy-800">
          {{ title }}
        </h2>
        <button
          type="button"
          class="flex h-8 w-8 items-center justify-center rounded-full text-slate-400
                 transition-colors hover:bg-navy-800/8 hover:text-navy-800"
          aria-label="Cerrar"
          @click="emit('close')"
        >
          <svg
            class="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Formulario -->
      <form class="mt-5 flex flex-col gap-4" @submit.prevent="onSubmit">
        <!-- Nombre -->
        <div>
          <label
            for="center-nombre"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Nombre del centro
          </label>
          <input
            id="center-nombre"
            v-model="nombre"
            type="text"
            required
            placeholder="Ej: Centro de Acopio Cruz Roja"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Dirección -->
        <div>
          <label
            for="center-direccion"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Dirección
          </label>
          <input
            id="center-direccion"
            v-model="direccion"
            type="text"
            required
            placeholder="Calle, número, comuna"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Zona -->
        <div>
          <label
            for="center-zona"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Zona
          </label>
          <input
            id="center-zona"
            v-model="zona"
            type="text"
            required
            placeholder="Ciudad o sector"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Horario de atención (opcional) -->
        <div>
          <label
            for="center-horario"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Horario de atención <span class="text-slate-400">(opcional)</span>
          </label>
          <input
            id="center-horario"
            v-model="horarioAtencion"
            type="text"
            placeholder="Ej: Lunes a Domingo 08:00 - 20:00"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
        </div>

        <!-- Emergencia a la que responde (opcional) -->
        <div>
          <label
            for="center-emergencia"
            class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
          >
            Emergencia <span class="text-slate-400">(opcional)</span>
          </label>
          <select
            id="center-emergencia"
            v-model="emergencyId"
            class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                   ring-1 ring-navy-600/20 transition-shadow
                   focus:outline-none focus:ring-2 focus:ring-navy-600"
          >
            <option value="">Sin emergencia</option>
            <option v-for="opt in emergencyOptions" :key="opt.id" :value="opt.id">
              {{ opt.label }}
            </option>
          </select>
          <p class="mt-1 text-xs text-slate-500">
            Elige el evento específico que tu centro está cubriendo, si aplica.
          </p>
        </div>

        <!-- Ubicación en el mapa (RF-05): geocodifica la dirección o marca a mano -->
        <div>
          <div class="flex items-center justify-between gap-2">
            <label class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600">
              Ubicación en el mapa <span class="text-slate-400">(opcional)</span>
            </label>
            <button
              v-if="props.geocode"
              type="button"
              class="shrink-0 rounded-lg border border-navy-600/25 px-3 py-1.5 text-xs font-semibold
                     text-navy-600 transition hover:bg-navy-600/10 disabled:cursor-not-allowed
                     disabled:opacity-50"
              :disabled="!canGeocode || geocoding"
              @click="onGeocodeAddress"
            >
              {{ geocoding ? 'Buscando…' : 'Ubicar por dirección' }}
            </button>
          </div>
          <p class="mt-1 text-xs text-slate-500">
            Usa "Ubicar por dirección" o haz click en el mapa para marcar el punto
            exacto; puedes arrastrar el pin para ajustarlo.
          </p>
          <div class="mt-2">
            <LocationPicker
              :latitud="pickerLat"
              :longitud="pickerLng"
              @pick="onPickFromMap"
            />
          </div>
          <p v-if="geocodeError" class="mt-1 text-xs text-amber-600">
            {{ geocodeError }}
          </p>
        </div>

        <!-- Coordenadas (reflejan el pin; editables para ajuste fino, ambas o ninguna) -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label
              for="center-lat"
              class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
            >
              Latitud <span class="text-slate-400">(opcional)</span>
            </label>
            <input
              id="center-lat"
              v-model="latitud"
              type="number"
              step="any"
              placeholder="-37.4697"
              class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                     placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                     focus:outline-none focus:ring-2 focus:ring-navy-600"
            >
          </div>
          <div>
            <label
              for="center-lng"
              class="block font-display text-sm font-bold uppercase tracking-widest text-navy-600"
            >
              Longitud <span class="text-slate-400">(opcional)</span>
            </label>
            <input
              id="center-lng"
              v-model="longitud"
              type="number"
              step="any"
              placeholder="-72.3522"
              class="mt-1 w-full rounded-lg bg-white px-3 py-2.5 text-sm text-navy-900
                     placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                     focus:outline-none focus:ring-2 focus:ring-navy-600"
            >
          </div>
        </div>
        <p v-if="coordsHint" class="-mt-2 text-xs text-amber-600">
          {{ coordsHint }}
        </p>

        <!-- Acciones -->
        <div class="mt-2 flex gap-3">
          <BaseButton
            variant="ghost"
            size="md"
            :full-width="true"
            class="border border-navy-600/25"
            @click="emit('close')"
          >
            Cancelar
          </BaseButton>
          <BaseButton
            type="submit"
            variant="navy"
            size="md"
            :full-width="true"
            :disabled="!isValid || isSubmitting"
          >
            {{ submitLabel }}
          </BaseButton>
        </div>

        <!-- Error de envío (409/422 del backend) -->
        <p v-if="submitError" class="text-sm text-alert">
          {{ submitError }}
        </p>
      </form>
    </div>
  </div>
</template>
