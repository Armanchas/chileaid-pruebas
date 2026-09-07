<script setup lang="ts">
import { computed, ref } from 'vue'
import CenterHeader from '~/components/donor/center/CenterHeader.vue'
import NeedUrgentCard from '~/components/donor/center/NeedUrgentCard.vue'
import NeedListItem from '~/components/donor/center/NeedListItem.vue'
import CenterInfoSection from '~/components/donor/center/CenterInfoSection.vue'
import BaseButton from '~/components/ui/BaseButton.vue'
import type { CenterDetailDTO } from '~/services/donorCentersService'

/**
 * VIEW — Orquesta el detalle completo de un centro. Puramente visual: recibe
 * todo por props y reparte a las secciones, comunicando intenciones por
 * eventos. No conoce servicios ni composables; segmentar las necesidades y el
 * colapsable de completadas son estado/lógica de presentación.
 */
const props = defineProps<{
  center: CenterDetailDTO | null
  isLoading: boolean
  error: string | null
}>()

const emit = defineEmits<{
  'go-back': []
  donate: []
  'open-map': []
}>()

/** Necesidades urgentes y activas: tarjetas destacadas. */
const urgentNeeds = computed(() =>
  (props.center?.necesidades ?? []).filter((n) => n.urgente && n.estado === 'activa')
)

/** Necesidades no urgentes y activas: requerimientos continuos. */
const otherNeeds = computed(() =>
  (props.center?.necesidades ?? []).filter((n) => !n.urgente && n.estado === 'activa')
)

/** Necesidades cuya meta ya se cumplió. */
const completedNeeds = computed(() =>
  (props.center?.necesidades ?? []).filter((n) => n.estado === 'completada')
)

/** Estado de UI del bloque colapsable de completadas (por defecto cerrado). */
const showCompleted = ref(false)
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
    <!-- Estado error -->
    <p
      v-if="error"
      role="alert"
      class="rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
    >
      {{ error }}
    </p>

    <!-- Estado loading: skeleton -->
    <div v-else-if="isLoading">
      <div class="h-32 animate-pulse rounded-2xl bg-navy-800/6" />
      <div class="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="n in 3"
          :key="n"
          class="h-48 animate-pulse rounded-2xl bg-navy-800/6"
        />
      </div>
    </div>

    <!-- Datos cargados -->
    <div v-else-if="center" class="flex flex-col gap-10">
      <!-- 1. Encabezado -->
      <CenterHeader
        :nombre="center.nombre"
        :organizacion="center.organizacion"
        :region="center.region"
        :direccion="center.direccion"
        :horario="center.horario"
        :estado="center.estado"
        :tipo-centro="center.tipoCentro"
        :emergencia="center.emergencia"
        :cobertura="center.cobertura"
        @go-back="emit('go-back')"
      />

      <!-- CTA principal: abre el flujo de donación al centro completo -->
      <div>
        <BaseButton
          variant="navy"
          :disabled="center.estado === 'cerrado'"
          @click="emit('donate')"
        >
          {{ center.estado === 'cerrado' ? 'Centro cerrado' : 'Donar a este centro' }}
        </BaseButton>
        <p v-if="center.estado !== 'cerrado'" class="mt-2 text-sm text-slate-500">
          Elige cuánto aportar de cada necesidad en un solo paso.
        </p>
      </div>

      <!-- 2. Necesidades urgentes -->
      <section v-if="urgentNeeds.length > 0">
        <div class="mb-6 border-b border-navy-800/10 pb-2">
          <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Necesidades Urgentes
          </h2>
          <p class="mt-1 text-sm text-slate-500">
            Elementos críticos con menor cobertura
          </p>
        </div>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <NeedUrgentCard
            v-for="need in urgentNeeds"
            :key="need.id"
            :need="need"
          />
        </div>
      </section>

      <!-- 3. Otras necesidades -->
      <section v-if="otherNeeds.length > 0">
        <div class="mb-6 border-b border-navy-800/10 pb-2">
          <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Otras Necesidades
          </h2>
          <p class="mt-1 text-sm text-slate-500">
            Requerimientos continuos
          </p>
        </div>
        <div class="glass-auth rounded-2xl px-5 py-2">
          <NeedListItem
            v-for="need in otherNeeds"
            :key="need.id"
            :need="need"
          />
        </div>
      </section>

      <!-- 4. Necesidades completadas (colapsable) -->
      <section v-if="completedNeeds.length > 0">
        <button
          type="button"
          class="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-500"
          :aria-expanded="showCompleted"
          @click="showCompleted = !showCompleted"
        >
          <svg
            class="h-4 w-4 transition-transform duration-200"
            :class="showCompleted ? 'rotate-90' : ''"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M9 6l6 6-6 6" />
          </svg>
          Ver necesidades completadas ({{ completedNeeds.length }})
        </button>
        <div v-if="showCompleted" class="glass-auth mt-3 rounded-2xl px-5 py-2">
          <NeedListItem
            v-for="need in completedNeeds"
            :key="need.id"
            :need="need"
          />
        </div>
      </section>

      <!-- 5. Información operativa -->
      <CenterInfoSection
        :coordinador="center.coordinador"
        :telefono="center.telefono"
        @open-map="emit('open-map')"
      />
    </div>

    <!-- Estado vacío (sin error y sin centro) -->
    <div
      v-else
      class="flex flex-col items-center justify-center rounded-2xl border border-navy-800/10 py-16 text-center"
    >
      <svg
        class="h-10 w-10 text-slate-400"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="M21 21l-4.3-4.3" />
      </svg>
      <p class="mt-3 text-slate-400">
        No se encontró el centro solicitado
      </p>
    </div>
  </div>
</template>
