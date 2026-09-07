<script setup lang="ts">
import { computed } from 'vue'
import QrcodeVue from 'qrcode.vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import type { CenterDetailDTO, NeedDTO } from '~/services/donorCentersService'
import type { DonationDTO } from '~/services/donationService'

/**
 * VIEW — Flujo de donación a un centro. Puramente visual: recibe todo por props
 * y comunica intenciones por eventos. No conoce servicios ni composables. El
 * mapeo cobertura→color, el cálculo de "faltan X" y el armado del resumen son
 * lógica de presentación.
 *
 * Dos pantallas en una: el formulario de selección (`!submitted`) y la
 * confirmación con el código de seguimiento (`submitted && donation`).
 */
const props = defineProps<{
  center: CenterDetailDTO | null
  donation: DonationDTO | null
  quantities: Record<string, number>
  canSubmit: boolean
  hasSelection: boolean
  isLoading: boolean
  isSubmitting: boolean
  submitted: boolean
  error: string | null
}>()

const emit = defineEmits<{
  'update:quantities': [needId: string, value: number]
  submit: []
  'go-back': []
  'go-tracking': []
}>()

/** Necesidades activas del centro: las únicas que se ofrecen para donar. */
const activeNeeds = computed<NeedDTO[]>(() =>
  (props.center?.necesidades ?? []).filter((n) => n.estado === 'activa')
)

/**
 * Resumen de lo seleccionado: necesidades activas con cantidad > 0, ya con su
 * cantidad resuelta desde el mapa de quantities.
 */
const resumen = computed(() =>
  activeNeeds.value
    .map((need) => ({ need, cantidad: props.quantities[need.id] ?? 0 }))
    .filter((row) => row.cantidad > 0)
)

/** Clase Tailwind de la barra de cobertura de un ítem (rojo/ámbar/verde). */
function barClass(cobertura: number): string {
  if (cobertura >= 70) return 'bg-green-500'
  if (cobertura >= 30) return 'bg-amber-400'
  return 'bg-red-500'
}

/** Ancho de la barra de cobertura, acotado a 0-100. */
function barWidth(cobertura: number): string {
  return `${Math.min(100, Math.max(0, cobertura))}%`
}

/** Unidades que aún faltan para cubrir la meta del ítem. */
function faltan(need: NeedDTO): number {
  return Math.max(0, need.cantidadRequerida - need.cantidadComprometida)
}

/** Normaliza el valor del input a un número no negativo antes de emitir. */
function onQuantityInput(needId: string, raw: string): void {
  const value = Math.max(0, Number(raw) || 0)
  emit('update:quantities', needId, value)
}
</script>

<template>
  <div class="min-h-screen bg-[#f0f4ff]">
    <div class="mx-auto max-w-3xl px-4 py-6 sm:px-6">
      <!-- Estado loading: skeletons -->
      <div v-if="isLoading" class="flex flex-col gap-6">
        <div class="h-10 w-48 animate-pulse rounded-lg bg-slate-200" />
        <div class="h-64 animate-pulse rounded-2xl bg-slate-200" />
        <div class="h-32 animate-pulse rounded-2xl bg-slate-200" />
      </div>

      <!-- Estado confirmación -->
      <div v-else-if="submitted && donation" class="py-6">
        <div class="glass-auth mx-auto max-w-md rounded-2xl px-6 py-8 text-center">
          <!-- Check -->
          <span
            class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100"
            aria-hidden="true"
          >
            <svg
              class="h-7 w-7"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#16a34a"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M20 6L9 17l-5-5" />
            </svg>
          </span>

          <h1 class="mt-4 font-display text-2xl font-black uppercase tracking-wide text-navy-800">
            ¡Donación comprometida!
          </h1>
          <p class="mt-1 text-sm text-slate-500">
            Centro: {{ donation.centerNombre }}
          </p>

          <hr class="my-6 border-navy-800/10">

          <p class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Código de seguimiento
          </p>
          <QrcodeVue
            :value="donation.codigoSeguimiento"
            :size="180"
            class="mx-auto my-3"
          />
          <p
            class="mt-3 rounded-lg border border-blue-200 bg-blue-50 px-6 py-3
                   text-center font-mono text-2xl font-bold tracking-widest text-navy-800"
          >
            {{ donation.codigoSeguimiento }}
          </p>

          <!-- Ítems donados -->
          <ul class="mt-5 space-y-1 text-left text-sm text-slate-500">
            <li
              v-for="item in donation.items"
              :key="item.needId"
              class="flex items-baseline justify-between gap-3"
            >
              <span>{{ item.needNombre }}</span>
              <span class="shrink-0 font-semibold text-navy-800">
                {{ item.cantidad }} {{ item.unidad }}
              </span>
            </li>
          </ul>

          <p class="mt-6 text-sm text-slate-500">
            Guarda este código. Lo necesitarás al momento de entregar tu donación
            en el centro.
          </p>

          <div class="mt-6 flex flex-col gap-3">
            <BaseButton variant="navy" full-width @click="emit('go-tracking')">
              Ver mis donaciones
            </BaseButton>
            <BaseButton variant="ghost" full-width @click="emit('go-back')">
              Volver al centro
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- Estado formulario -->
      <div v-else class="flex flex-col gap-6">
        <!-- Header -->
        <header>
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
            Volver al centro
          </button>
          <h1 class="mt-3 font-display text-3xl font-black uppercase tracking-wide text-navy-800">
            Comprometer donación
          </h1>
          <p v-if="center" class="mt-1 text-slate-500">
            {{ center.nombre }} · {{ center.zona }}
          </p>
        </header>

        <!-- Lista de necesidades activas -->
        <section class="glass-auth rounded-2xl p-5 sm:p-6">
          <div class="mb-5 border-b border-navy-800/10 pb-2">
            <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
              ¿Qué vas a donar?
            </h2>
            <p class="mt-1 text-sm text-slate-500">
              Indica cuánto puedes aportar de cada ítem
            </p>
          </div>

          <div class="flex flex-col divide-y divide-navy-800/8">
            <div
              v-for="need in activeNeeds"
              :key="need.id"
              class="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:gap-5"
            >
              <!-- Info del ítem -->
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <span
                    v-if="need.urgente"
                    class="inline-flex items-center gap-1 text-xs font-semibold text-red-600"
                  >
                    <span class="alert-pulse h-2 w-2 rounded-full bg-red-500" aria-hidden="true" />
                    Urgente
                  </span>
                  <span class="text-xs uppercase tracking-widest text-slate-500">
                    {{ need.categoria }}
                  </span>
                </div>
                <p class="mt-1 font-medium text-navy-800">
                  {{ need.nombre }}
                </p>

                <!-- Barra de cobertura compacta -->
                <div class="mt-2 h-1.5 w-full max-w-xs overflow-hidden rounded-full bg-navy-800/8">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="barClass(need.cobertura)"
                    :style="{ width: barWidth(need.cobertura) }"
                  />
                </div>
                <p class="mt-1.5 text-xs text-slate-500">
                  Faltan {{ faltan(need) }} {{ need.unidad }}
                </p>
              </div>

              <!-- Input de cantidad -->
              <div class="shrink-0 sm:w-32">
                <input
                  type="number"
                  min="0"
                  inputmode="numeric"
                  placeholder="0"
                  :value="quantities[need.id]"
                  :disabled="need.cobertura >= 100"
                  class="w-full rounded-lg border border-navy-800/15 bg-white px-3 py-2
                         text-right text-navy-900 placeholder:text-slate-400
                         focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20
                         disabled:cursor-not-allowed disabled:bg-slate-100"
                  :aria-label="`Cantidad de ${need.nombre} en ${need.unidad}`"
                  @input="onQuantityInput(need.id, ($event.target as HTMLInputElement).value)"
                >
                <p
                  v-if="need.cobertura >= 100"
                  class="mt-1 text-right text-xs text-slate-400"
                >
                  Meta cumplida
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- Resumen de selección -->
        <section v-if="hasSelection" class="glass-auth rounded-2xl p-5 sm:p-6">
          <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Tu donación incluye:
          </h2>
          <ul class="mt-3 space-y-1.5">
            <li
              v-for="row in resumen"
              :key="row.need.id"
              class="text-sm text-navy-800"
            >
              {{ row.cantidad }} {{ row.need.unidad }} de {{ row.need.nombre }}
            </li>
          </ul>
        </section>

        <!-- Footer: error + confirmar -->
        <footer class="flex flex-col gap-3">
          <p
            v-if="error"
            role="alert"
            class="text-sm font-semibold text-red-600"
          >
            {{ error }}
          </p>
          <BaseButton
            variant="navy"
            full-width
            :disabled="!canSubmit"
            class="sm:w-auto sm:self-end"
            @click="emit('submit')"
          >
            {{ isSubmitting ? 'Enviando…' : 'Confirmar donación' }}
          </BaseButton>
        </footer>
      </div>
    </div>
  </div>
</template>
