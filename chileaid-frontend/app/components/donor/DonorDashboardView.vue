<script setup lang="ts">
import { computed } from 'vue'
import DonorEmergencyCard from '~/components/donor/DonorEmergencyCard.vue'
import DonorCenterCard from '~/components/donor/DonorCenterCard.vue'
import type { CenterDTO, EmergencyDTO } from '~/services/donorCentersService'

/**
 * VIEW — Orquesta la vista completa del panel del donante. Puramente visual:
 * recibe todo por props y reparte a las tarjetas, comunicando intenciones por
 * eventos. No conoce servicios ni composables; el orden y los derivados que usa
 * son lógica de presentación.
 */
const props = defineProps<{
  emergencies: EmergencyDTO[]
  criticalCenters: CenterDTO[]
  isLoading: boolean
  error: string | null
  userName: string
}>()

const emit = defineEmits<{
  'select-emergency': [emergency: EmergencyDTO]
  'select-center': [id: string]
}>()

/** Hay al menos un centro en estado crítico (para el banner de alerta). */
const hasCriticalCenters = computed(() =>
  props.criticalCenters.some((c) => c.estado === 'critico')
)

/** Centros ordenados por cobertura ascendente: los más urgentes primero. */
const sortedCenters = computed(() =>
  [...props.criticalCenters].sort((a, b) => a.cobertura - b.cobertura)
)

const hasEmergencies = computed(() => props.emergencies.length > 0)
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
    <!-- 1. Header de bienvenida -->
    <header>
      <h1 class="font-display text-3xl font-black uppercase text-navy-800">
        Hola, {{ userName }}
      </h1>
      <p class="mt-1 text-slate-500">
        Estas son las emergencias activas en Chile
      </p>

      <p
        v-if="hasCriticalCenters"
        role="status"
        class="mt-4 rounded-xl bg-alert/8 px-4 py-3 text-sm font-semibold text-alert"
      >
        ⚠ Hay centros en estado crítico que necesitan ayuda urgente
      </p>
    </header>

    <!-- Error de carga -->
    <p
      v-if="error"
      role="alert"
      class="mt-6 rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
    >
      {{ error }}
    </p>

    <!-- 2. Sección: Emergencias activas -->
    <section class="mt-8">
      <div class="mb-4 flex items-center gap-3">
        <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Emergencias activas
        </h2>
        <span class="h-px flex-1 bg-navy-800/15" />
      </div>

      <!-- Loading: skeletons -->
      <div v-if="isLoading" class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div
          v-for="n in 2"
          :key="n"
          class="h-40 animate-pulse rounded-2xl bg-navy-800/6"
        />
      </div>

      <!-- Datos -->
      <div v-else-if="hasEmergencies" class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <DonorEmergencyCard
          v-for="emergency in emergencies"
          :key="emergency.id"
          :emergency="emergency"
          @select="() => emit('select-emergency', emergency)"
        />
      </div>

      <!-- Vacío -->
      <div
        v-else
        class="flex flex-col items-center justify-center rounded-2xl border border-navy-800/10 py-12 text-center"
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
          <path d="M9 12l2 2 4-4" />
          <circle cx="12" cy="12" r="9" />
        </svg>
        <p class="mt-3 text-slate-400">
          No hay emergencias activas en este momento
        </p>
      </div>
    </section>

    <!-- 3. Sección: Centros más urgentes -->
    <section class="mt-10">
      <div class="mb-4 flex items-center gap-3">
        <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Centros más urgentes
        </h2>
        <span class="h-px flex-1 bg-navy-800/15" />
      </div>

      <!-- Loading: skeletons -->
      <div v-if="isLoading" class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="n in 3"
          :key="n"
          class="h-40 animate-pulse rounded-2xl bg-navy-800/6"
        />
      </div>

      <!-- Datos: scroll horizontal en mobile, grid 1-2-3 en desktop -->
      <div
        v-else
        class="flex gap-4 overflow-x-auto pb-2 md:grid md:grid-cols-2 md:overflow-visible md:pb-0 lg:grid-cols-3"
      >
        <div
          v-for="center in sortedCenters"
          :key="center.id"
          class="w-[280px] shrink-0 md:w-auto"
        >
          <DonorCenterCard
            :center="center"
            @select="(id) => emit('select-center', id)"
          />
        </div>
      </div>
    </section>
  </div>
</template>
