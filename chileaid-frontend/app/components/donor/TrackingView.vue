<script setup lang="ts">
import QrcodeVue from 'qrcode.vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import type {
  DonationDTO,
  DonationEstado,
  MotivoCancelacion
} from '~/services/donationService'

/**
 * VIEW — Historial de donaciones del donante con timeline de estado y QR de
 * seguimiento. Puramente visual: recibe todo por props (`donations` ya es la
 * página actual, paginada server-side por el ViewModel; `total` es el conteo
 * completo del donante) y comunica intenciones por eventos. No conoce
 * servicios ni composables. El mapeo estado→badge/paso es presentación.
 */
defineProps<{
  donations: DonationDTO[]
  total: number
  isLoading: boolean
  error: string | null
  activeQRCode: string | null
  currentPage: number
  totalPages: number
  hasNextPage: boolean
  hasPrevPage: boolean
  cancellingId: string | null
}>()

const emit = defineEmits<{
  'next-page': []
  'prev-page': []
  'open-qr': [codigoSeguimiento: string]
  'close-qr': []
  'go-profile': []
  cancel: [id: string]
}>()

/**
 * Mensaje del ítem cancelado según quién disparó la cancelación (el backend lo
 * marca en `motivoCancelacion`). Deja claro al donante por qué su aporte no sigue.
 */
const MOTIVO_LABEL: Record<MotivoCancelacion, string> = {
  donante: 'Cancelado por ti',
  cierre_necesidad: 'La organización cerró esta necesidad'
}

/** Pide confirmación antes de emitir la cancelación (patrón de la UI del proyecto). */
function onCancel(id: string): void {
  if (window.confirm('¿Seguro que quieres cancelar esta donación? No se puede deshacer.')) {
    emit('cancel', id)
  }
}

/** Clases del badge de estado (mismos colores semánticos que ProfileView). */
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
</script>

<template>
  <div class="min-h-screen bg-[#f0f4ff]">
    <div class="mx-auto max-w-3xl px-4 py-6 sm:px-6">
      <!-- Header -->
      <header class="mb-6">
        <button
          type="button"
          class="flex items-center gap-1.5 text-sm font-semibold text-navy-600 hover:text-navy-800"
          @click="emit('go-profile')"
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
          Volver al perfil
        </button>
        <h1 class="mt-3 font-display text-3xl font-black uppercase tracking-wide text-navy-800">
          Mis donaciones
        </h1>
        <p class="mt-1 text-slate-500">
          {{ total }}
          {{ total === 1 ? 'donación registrada' : 'donaciones registradas' }}
        </p>
      </header>

      <!-- Estado error -->
      <p
        v-if="error"
        role="alert"
        class="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-600"
      >
        {{ error }}
      </p>

      <!-- Estado loading: skeletons -->
      <div v-else-if="isLoading" class="flex flex-col gap-4">
        <div
          v-for="n in 3"
          :key="n"
          class="h-48 animate-pulse rounded-2xl bg-slate-200"
        />
      </div>

      <!-- Estado vacío -->
      <div
        v-else-if="total === 0"
        class="glass-auth rounded-2xl px-6 py-12 text-center"
      >
        <p class="text-sm text-slate-500">
          Aún no has realizado ninguna donación.
        </p>
      </div>

      <!-- Lista paginada -->
      <div v-else class="flex flex-col gap-4">
        <article
          v-for="donation in donations"
          :key="donation.id"
          class="glass-auth rounded-2xl p-5 sm:p-6"
        >
          <!-- Fila superior: estado + código + fecha -->
          <div class="flex items-start justify-between gap-3">
            <div class="flex flex-wrap items-center gap-3">
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
            <span class="shrink-0 text-xs text-slate-400">
              {{ donation.fechaCreacion }}
            </span>
          </div>

          <!-- Mensaje de agradecimiento cuando el centro ya recibió el aporte -->
          <p
            v-if="donation.estado === 'recibido'"
            class="mt-1.5 text-xs text-teal-700"
          >
            Gracias por tu aporte
          </p>

          <!-- Centro -->
          <p class="mt-2 text-sm text-slate-500">
            {{ donation.centerNombre }}
          </p>

          <!-- Ítems donados (los cancelados se muestran tachados con su motivo) -->
          <ul class="mt-4 space-y-1 text-xs text-slate-500">
            <li
              v-for="item in donation.items"
              :key="item.needId"
              class="flex flex-wrap items-center gap-x-2"
            >
              <span :class="{ 'text-slate-400 line-through': !item.activo }">
                {{ item.cantidad }} {{ item.unidad }} de {{ item.needNombre }}
              </span>
              <span
                v-if="!item.activo && item.motivoCancelacion"
                class="text-[11px] font-semibold text-slate-400"
              >
                · {{ MOTIVO_LABEL[item.motivoCancelacion] }}
              </span>
            </li>
          </ul>

          <!-- Acciones: ver QR y (solo si sigue pendiente) cancelar -->
          <div class="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              class="rounded-lg border border-navy-800/15 px-3 py-1.5 text-xs font-semibold
                     text-navy-600 transition-colors hover:bg-navy-600/10"
              @click="emit('open-qr', donation.codigoSeguimiento)"
            >
              Ver QR
            </button>
            <button
              v-if="donation.estado === 'pendiente'"
              type="button"
              :disabled="cancellingId === donation.id"
              class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold
                     text-slate-600 transition-colors hover:bg-slate-100 disabled:opacity-50"
              @click="onCancel(donation.id)"
            >
              {{ cancellingId === donation.id ? 'Cancelando…' : 'Cancelar donación' }}
            </button>
          </div>
        </article>

        <!-- Paginación -->
        <nav
          v-if="totalPages > 1"
          class="mt-2 flex items-center justify-center gap-4"
          aria-label="Paginación"
        >
          <BaseButton
            variant="ghost"
            :disabled="!hasPrevPage"
            @click="emit('prev-page')"
          >
            ← Anterior
          </BaseButton>
          <span class="text-sm text-slate-500">
            Página {{ currentPage }} de {{ totalPages }}
          </span>
          <BaseButton
            variant="ghost"
            :disabled="!hasNextPage"
            @click="emit('next-page')"
          >
            Siguiente →
          </BaseButton>
        </nav>
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
