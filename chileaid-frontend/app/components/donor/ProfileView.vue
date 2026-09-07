<script setup lang="ts">
import { computed } from 'vue'
import QrcodeVue from 'qrcode.vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import type { DonorProfileDTO } from '~/services/profileService'
import type { DonationDTO, DonationEstado } from '~/services/donationService'

/**
 * VIEW — Perfil del donante: datos personales editables + historial de
 * donaciones con su QR de seguimiento. Puramente visual: recibe todo por props y
 * comunica intenciones por eventos. No conoce servicios ni composables. El mapeo
 * estado→badge, las iniciales del avatar y el recorte de ítems son presentación.
 */
const props = defineProps<{
  profile: DonorProfileDTO | null
  totalDonaciones: number
  form: { nombre: string; apellido: string; email: string }
  isSaving: boolean
  saveSuccess: boolean
  saveError: string | null
  isLoading: boolean
  error: string | null
  activeQRCode: string | null
  recentDonations: DonationDTO[]
}>()

const emit = defineEmits<{
  'update:form': [field: 'nombre' | 'apellido' | 'email', value: string]
  save: []
  'open-qr': [codigoSeguimiento: string]
  'close-qr': []
  'go-back': []
  'go-tracking': []
}>()

/** Clases del badge de estado de una donación (mismos estados que TrackingView). */
const ESTADO_BADGE: Record<DonationEstado, string> = {
  pendiente: 'bg-amber-100 text-amber-700',
  recibido: 'bg-teal-100 text-teal-800',
  cancelada: 'bg-slate-200 text-slate-600'
}

/** Etiqueta legible en español de cada estado. */
const ESTADO_LABEL: Record<DonationEstado, string> = {
  pendiente: 'Pendiente de entrega',
  recibido: 'Recibido por el centro ✓',
  cancelada: 'Cancelada'
}

/** Iniciales del avatar a partir del formulario (reaccionan al escribir). */
const iniciales = computed(() => {
  const n = props.form.nombre.trim().charAt(0)
  const a = props.form.apellido.trim().charAt(0)
  return (n + a).toUpperCase()
})

/** Primeros dos ítems de una donación (los visibles en la fila). */
function visibleItems(donation: DonationDTO): DonationDTO['items'] {
  return donation.items.slice(0, 2)
}

/** Cantidad de ítems ocultos más allá de los dos primeros. */
function extraItems(donation: DonationDTO): number {
  return Math.max(0, donation.items.length - 2)
}

/** Reenvía el cambio de un campo del formulario hacia el ViewModel. */
function onFieldInput(field: 'nombre' | 'apellido' | 'email', event: Event): void {
  emit('update:form', field, (event.target as HTMLInputElement).value)
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
          Mi perfil
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
      <div v-else-if="isLoading" class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div class="h-96 animate-pulse rounded-2xl bg-slate-200" />
        <div class="h-72 animate-pulse rounded-2xl bg-slate-200" />
      </div>

      <!-- Contenido -->
      <div v-else class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <!-- Columna izquierda: datos personales -->
        <section class="glass-auth rounded-2xl p-5 sm:p-6">
          <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Mis datos
          </h2>

          <!-- Avatar -->
          <div class="mt-5 flex items-center gap-4">
            <span
              class="flex h-16 w-16 items-center justify-center rounded-full bg-navy-800
                     font-display text-xl font-black uppercase text-white"
              aria-hidden="true"
            >
              {{ iniciales }}
            </span>
            <div class="min-w-0">
              <p class="truncate font-display text-lg font-bold uppercase text-navy-800">
                {{ form.nombre }} {{ form.apellido }}
              </p>
              <p class="truncate text-sm text-slate-500">
                {{ form.email }}
              </p>
            </div>
          </div>

          <!-- Formulario -->
          <div class="mt-6 flex flex-col gap-4">
            <div>
              <label
                for="profile-nombre"
                class="block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
              >
                Nombre
              </label>
              <input
                id="profile-nombre"
                type="text"
                :value="form.nombre"
                placeholder="Tu nombre"
                class="mt-1.5 w-full rounded-lg border border-navy-800/15 bg-white px-3 py-2
                       text-navy-900 placeholder:text-slate-400
                       focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20"
                @input="onFieldInput('nombre', $event)"
              >
            </div>

            <div>
              <label
                for="profile-apellido"
                class="block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
              >
                Apellido
              </label>
              <input
                id="profile-apellido"
                type="text"
                :value="form.apellido"
                placeholder="Tu apellido"
                class="mt-1.5 w-full rounded-lg border border-navy-800/15 bg-white px-3 py-2
                       text-navy-900 placeholder:text-slate-400
                       focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20"
                @input="onFieldInput('apellido', $event)"
              >
            </div>

            <div>
              <label
                for="profile-email"
                class="block font-display text-xs font-bold uppercase tracking-widest text-navy-600"
              >
                Correo electrónico
              </label>
              <input
                id="profile-email"
                type="email"
                :value="form.email"
                placeholder="tucorreo@ejemplo.cl"
                class="mt-1.5 w-full rounded-lg border border-navy-800/15 bg-white px-3 py-2
                       text-navy-900 placeholder:text-slate-400
                       focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20"
                @input="onFieldInput('email', $event)"
              >
            </div>

            <!-- Cambiar contraseña (placeholder sin acción) -->
            <button
              type="button"
              class="self-start text-sm font-semibold text-slate-500 hover:text-navy-600"
            >
              Cambiar contraseña
            </button>

            <!-- Feedback de guardado -->
            <p v-if="saveSuccess" class="text-sm font-semibold text-green-600">
              ✓ Cambios guardados
            </p>
            <p v-else-if="saveError" class="text-sm font-semibold text-red-600">
              {{ saveError }}
            </p>

            <BaseButton
              variant="navy"
              full-width
              :disabled="isSaving"
              @click="emit('save')"
            >
              {{ isSaving ? 'Guardando…' : 'Guardar cambios' }}
            </BaseButton>
          </div>
        </section>

        <!-- Columna derecha: mis donaciones -->
        <section class="glass-auth rounded-2xl p-5 sm:p-6">
          <div class="flex items-center justify-between gap-3">
            <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
              Mis donaciones
            </h2>
            <button
              type="button"
              class="shrink-0 text-sm font-semibold text-navy-600 hover:text-navy-800"
              @click="emit('go-tracking')"
            >
              Ver historial →
            </button>
          </div>

          <p v-if="totalDonaciones === 0" class="mt-5 text-sm text-slate-500">
            Aún no has realizado ninguna donación.
          </p>

          <ul v-else class="mt-5 flex flex-col divide-y divide-navy-800/8">
            <li
              v-for="donation in recentDonations"
              :key="donation.id"
              class="flex flex-col gap-2 py-4 first:pt-0"
            >
              <!-- Estado + código -->
              <div class="flex items-center justify-between gap-3">
                <span
                  class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="ESTADO_BADGE[donation.estado]"
                >
                  {{ ESTADO_LABEL[donation.estado] }}
                </span>
                <span class="font-mono text-sm font-bold text-navy-800">
                  {{ donation.codigoSeguimiento }}
                </span>
              </div>

              <!-- Centro + fecha -->
              <div>
                <p class="text-xs text-slate-500">
                  {{ donation.centerNombre }}
                </p>
                <p class="text-xs text-slate-400">
                  {{ donation.fechaCreacion }}
                </p>
              </div>

              <!-- Ítems (máximo 2 + "+N más") -->
              <ul class="text-xs text-slate-500">
                <li v-for="item in visibleItems(donation)" :key="item.needId">
                  {{ item.cantidad }} {{ item.unidad }} de {{ item.needNombre }}
                </li>
                <li v-if="extraItems(donation) > 0" class="text-slate-400">
                  + {{ extraItems(donation) }} más
                </li>
              </ul>

              <!-- Ver QR -->
              <div>
                <button
                  type="button"
                  class="rounded-lg border border-navy-800/15 px-3 py-1.5 text-xs font-semibold
                         text-navy-600 transition-colors hover:bg-navy-600/10"
                  @click="emit('open-qr', donation.codigoSeguimiento)"
                >
                  Ver QR
                </button>
              </div>
            </li>
          </ul>

          <!-- Enlace al historial completo (solo si hay más de 5) -->
          <button
            v-if="totalDonaciones > 5"
            type="button"
            class="mt-4 text-sm font-semibold text-navy-600 underline hover:text-navy-800"
            @click="emit('go-tracking')"
          >
            Ver todas las donaciones →
          </button>
        </section>
      </div>
    </div>

    <!-- Modal QR -->
    <div
      v-if="activeQRCode !== null"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      @click.self="emit('close-qr')"
    >
      <div class="glass-auth mx-4 w-full max-w-xs rounded-2xl p-6 text-center">
        <h3 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Código QR
        </h3>

        <div class="mt-5 flex justify-center">
          <QrcodeVue :value="activeQRCode" :size="200" />
        </div>

        <p class="mt-5 text-center font-mono text-xl font-bold tracking-widest text-navy-800">
          {{ activeQRCode }}
        </p>
        <p class="mt-2 text-center text-sm text-slate-500">
          Muestra este código al entregar tu donación.
        </p>

        <BaseButton
          variant="navy"
          full-width
          class="mt-6"
          @click="emit('close-qr')"
        >
          Cerrar
        </BaseButton>
      </div>
    </div>
  </div>
</template>
