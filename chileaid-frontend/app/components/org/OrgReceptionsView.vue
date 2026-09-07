<script setup lang="ts">
import BaseButton from '~/components/ui/BaseButton.vue'
import type { PendingReceptionDTO } from '~/services/orgReceptionsService'

/**
 * VIEW — Confirmación de recepciones del centro (CU-07). Puramente visual: recibe
 * el estado por props y comunica intenciones por eventos. La org confirma una
 * donación por su código (manual; sin escáner QR). El total de una recepción es
 * lógica de presentación.
 */
const props = defineProps<{
  pendingReceptions: PendingReceptionDTO[]
  isLoading: boolean
  error: string | null
  receptionCode: string
  isConfirming: boolean
  confirmError: string | null
  confirmSuccess: string | null
  hasPendingReceptions: boolean
}>()

const emit = defineEmits<{
  'update:receptionCode': [value: string]
  'confirm-reception': [codigo: string]
  'go-back': []
}>()

/** Fecha legible (YYYY-MM-DD) a partir del ISO 8601 del compromiso. */
function fecha(iso: string): string {
  return iso.slice(0, 10)
}

/** Propaga el código tecleado al ViewModel. */
function onCodeInput(event: Event): void {
  emit('update:receptionCode', (event.target as HTMLInputElement).value)
}

function confirmManual(): void {
  if (props.receptionCode.trim() && !props.isConfirming) {
    emit('confirm-reception', props.receptionCode)
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-6">
    <!-- Encabezado -->
    <header class="mb-6">
      <button
        type="button"
        class="text-sm text-navy-600 hover:underline"
        @click="emit('go-back')"
      >
        ← Volver al panel
      </button>
      <h1 class="mt-2 font-display text-2xl font-black uppercase leading-tight text-navy-800">
        Confirmar recepciones
      </h1>
      <p class="mt-1 text-sm text-slate-500">
        Ingresa el código de seguimiento de la donación que llegó a tu centro, o
        confírmala desde la lista de pendientes.
      </p>
    </header>

    <!-- Confirmación por código manual -->
    <section class="glass-auth rounded-2xl p-5">
      <label for="reception-code" class="block text-xs text-slate-500">
        Código de seguimiento
      </label>
      <div class="mt-1 flex gap-2">
        <input
          id="reception-code"
          :value="receptionCode"
          type="text"
          placeholder="CA-XXXXXXXX"
          class="min-w-0 flex-1 rounded-lg bg-white px-3 py-2.5 font-mono text-sm text-navy-900
                 placeholder-slate-400 ring-1 ring-navy-600/20 transition-shadow
                 focus:outline-none focus:ring-2 focus:ring-navy-600"
          @input="onCodeInput"
          @keyup.enter="confirmManual"
        >
        <BaseButton
          variant="navy"
          size="md"
          :disabled="!receptionCode.trim() || isConfirming"
          @click="confirmManual"
        >
          {{ isConfirming ? 'Confirmando...' : 'Confirmar' }}
        </BaseButton>
      </div>

      <p v-if="confirmError" class="mt-2 text-sm text-alert">
        {{ confirmError }}
      </p>
      <p v-else-if="confirmSuccess" class="mt-2 text-sm text-green-600">
        ✓ {{ confirmSuccess }}
      </p>
    </section>

    <!-- Lista de pendientes -->
    <section class="mt-6">
      <div class="flex items-baseline justify-between">
        <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Recepciones pendientes
        </h2>
        <span class="text-sm text-slate-500">
          {{ pendingReceptions.length }}
        </span>
      </div>

      <!-- Error -->
      <p
        v-if="error"
        role="alert"
        class="mt-4 rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
      >
        {{ error }}
      </p>

      <!-- Loading -->
      <div v-else-if="isLoading" class="mt-4 flex flex-col gap-3">
        <div class="h-24 animate-pulse rounded-2xl bg-slate-200" />
        <div class="h-24 animate-pulse rounded-2xl bg-slate-200" />
      </div>

      <!-- Vacío -->
      <p
        v-else-if="!hasPendingReceptions"
        class="mt-4 rounded-2xl border border-navy-800/10 py-10 text-center text-sm text-slate-400"
      >
        No hay recepciones pendientes
      </p>

      <!-- Lista -->
      <ul v-else class="mt-4 flex flex-col gap-3">
        <li
          v-for="reception in pendingReceptions"
          :key="reception.donationId"
          class="glass-auth rounded-2xl p-4"
        >
          <div class="flex items-center justify-between gap-2">
            <span class="font-mono text-sm font-semibold text-navy-800">
              {{ reception.codigoSeguimiento }}
            </span>
            <span class="shrink-0 text-xs text-slate-400">
              {{ fecha(reception.createdAt) }}
            </span>
          </div>
          <ul class="mt-2 space-y-0.5">
            <li
              v-for="(item, i) in reception.items"
              :key="i"
              class="text-sm text-slate-600"
            >
              · {{ item.insumoNombre }}: {{ item.cantidad }}
            </li>
          </ul>
          <BaseButton
            variant="navy"
            size="md"
            :full-width="true"
            :disabled="isConfirming"
            class="mt-3"
            @click="emit('confirm-reception', reception.codigoSeguimiento)"
          >
            Confirmar esta recepción
          </BaseButton>
        </li>
      </ul>
    </section>
  </div>
</template>
