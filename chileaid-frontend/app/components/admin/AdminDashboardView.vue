<script setup lang="ts">
/**
 * VIEW — Panel de administración de la plataforma. Puramente visual: recibe todo
 * por props (estado ya derivado por el ViewModel) y comunica intenciones por
 * eventos. No conoce servicios ni composables; el formateo de fecha es lógica de
 * presentación y los mapeos de actividad (label/color) llegan como funciones desde
 * el ViewModel, vía la página.
 */
import BaseButton from '~/components/ui/BaseButton.vue'
import type {
  PlatformStatsDTO,
  RecentActivityItem
} from '~/services/adminDashboardService'

const props = defineProps<{
  stats: PlatformStatsDTO | null
  recentActivity: RecentActivityItem[]
  isLoading: boolean
  error: string | null
  tasaPendientes: number
  /** Mapeos puros provenientes del ViewModel (label/color del badge de actividad). */
  actividadLabel: (tipo: string) => string
  actividadColor: (tipo: string) => string
}>()

const emit = defineEmits<{
  'go-orgs': []
  'go-catalog': []
}>()

/** Formatea una fecha ISO `YYYY-MM-DD` como `dd/mm/yyyy`. */
function fechaFormateada(fecha: string): string {
  const [y, m, d] = fecha.split('-')
  return `${d}/${m}/${y}`
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6">
    <!-- Estado error -->
    <p
      v-if="error"
      role="alert"
      class="rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
    >
      {{ error }}
    </p>

    <div v-else class="flex flex-col gap-8">
      <!-- ===== SECCIÓN 1: MÉTRICAS GLOBALES ===== -->
      <section>
        <header class="mb-5">
          <h1 class="font-display text-2xl font-black uppercase leading-tight text-navy-800">
            Panel de administración
          </h1>
          <p class="mt-0.5 text-sm text-slate-500">
            Estado general de la plataforma Chile Aid
          </p>
        </header>

        <!-- Skeleton de carga: 6 cards -->
        <div v-if="isLoading || !stats" class="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div
            v-for="i in 6"
            :key="i"
            class="h-28 animate-pulse rounded-2xl bg-slate-200"
          />
        </div>

        <!-- Cards de métricas -->
        <div v-else class="grid grid-cols-2 gap-4 md:grid-cols-4">
          <!-- 1. Organizaciones activas -->
          <div class="glass-auth rounded-2xl p-5">
            <div class="flex flex-wrap items-baseline gap-2">
              <span class="font-display text-3xl font-black text-navy-800">
                {{ stats.organizacionesActivas }}
              </span>
              <span
                v-if="stats.organizacionesPendientes > 0"
                class="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700"
              >
                + {{ stats.organizacionesPendientes }} pendientes
              </span>
            </div>
            <p class="mt-1 text-sm text-slate-500">Organizaciones activas</p>
          </div>

          <!-- 2. Donaciones totales -->
          <div class="glass-auth rounded-2xl p-5">
            <span class="font-display text-3xl font-black text-navy-800">
              {{ stats.donacionesTotales }}
            </span>
            <p class="mt-1 text-sm text-slate-500">Donaciones totales</p>
            <p class="mt-1 text-xs text-green-600">
              + {{ stats.donacionesUltimos7Dias }} esta semana
            </p>
          </div>

          <!-- 3. Emergencias activas -->
          <div class="glass-auth rounded-2xl p-5">
            <span
              class="font-display text-3xl font-black"
              :class="stats.emergenciasActivas > 0 ? 'text-alert' : 'text-green-600'"
            >
              {{ stats.emergenciasActivas }}
            </span>
            <p class="mt-1 text-sm text-slate-500">Emergencias activas</p>
          </div>

          <!-- 4. Entregas realizadas -->
          <div class="glass-auth rounded-2xl p-5">
            <span class="font-display text-3xl font-black text-navy-800">
              {{ stats.entregasRealizadas }}
            </span>
            <p class="mt-1 text-sm text-slate-500">Entregas realizadas</p>
          </div>

          <!-- 5. Centros operativos -->
          <div class="glass-auth rounded-2xl p-5">
            <span class="font-display text-3xl font-black text-navy-800">
              {{ stats.centrosOperativos }}
            </span>
            <p class="mt-1 text-sm text-slate-500">Centros operativos</p>
          </div>

          <!-- 6. Orgs pendientes de revisión (tasa) -->
          <div class="glass-auth rounded-2xl p-5">
            <span class="font-display text-3xl font-black text-navy-800">
              {{ tasaPendientes }}%
            </span>
            <div class="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                class="h-full rounded-full bg-navy-600 transition-all duration-700"
                :style="{ width: `${Math.min(100, Math.max(0, tasaPendientes))}%` }"
              />
            </div>
            <p class="mt-2 text-sm text-slate-500">Orgs pendientes de revisión</p>
          </div>
        </div>
      </section>

      <!-- ===== SECCIÓN 2: ACTIVIDAD RECIENTE + ACCESOS RÁPIDOS ===== -->
      <section class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <!-- Columna izquierda: actividad reciente -->
        <div class="glass-auth rounded-2xl p-5">
          <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Actividad reciente
          </h2>

          <p v-if="recentActivity.length === 0" class="mt-4 text-sm text-slate-400">
            Sin actividad reciente
          </p>

          <ul v-else class="mt-4 flex flex-col divide-y divide-slate-100">
            <li
              v-for="item in recentActivity"
              :key="item.id"
              class="py-3 first:pt-0"
            >
              <div class="flex items-center justify-between gap-2">
                <span
                  class="shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="actividadColor(item.tipo)"
                >
                  {{ actividadLabel(item.tipo) }}
                </span>
                <span class="shrink-0 text-xs text-slate-400">
                  {{ fechaFormateada(item.fecha) }}
                </span>
              </div>
              <p class="mt-1.5 text-sm text-slate-600">
                {{ item.descripcion }}
              </p>
            </li>
          </ul>
        </div>

        <!-- Columna derecha: accesos rápidos -->
        <div class="glass-auth rounded-2xl p-5">
          <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
            Accesos rápidos
          </h2>

          <div class="mt-4 flex flex-col gap-3">
            <BaseButton
              variant="navy"
              size="lg"
              :full-width="true"
              @click="emit('go-orgs')"
            >
              Revisar organizaciones pendientes
              <span
                v-if="stats && stats.organizacionesPendientes > 0"
                class="ml-1 rounded-full bg-alert px-2 text-xs font-bold text-white"
              >
                {{ stats.organizacionesPendientes }}
              </span>
            </BaseButton>

            <BaseButton
              variant="ghost"
              size="lg"
              :full-width="true"
              class="border border-navy-600/25"
              @click="emit('go-catalog')"
            >
              Gestionar catálogo de insumos
            </BaseButton>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
