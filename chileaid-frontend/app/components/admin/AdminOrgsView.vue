<script setup lang="ts">
/**
 * VIEW — Gestión de organizaciones del administrador. Puramente visual: recibe
 * todo por props (estado ya derivado por el ViewModel) y comunica intenciones por
 * eventos. No conoce servicios ni composables; los mapeos de etiqueta/color de
 * `estado` y `tipo` y el formateo de fecha son lógica de presentación (mismo
 * patrón que OrgDashboardView).
 */
import BaseButton from '~/components/ui/BaseButton.vue'
import type { AdminDocumentDTO, AdminOrgDTO } from '~/services/adminOrgsService'

const props = defineProps<{
  orgs: AdminOrgDTO[]
  isLoading: boolean
  error: string | null
  filtroEstado: string
  conteosPorEstado: Record<string, number>
  currentPage: number
  totalPages: number
  hasNextPage: boolean
  hasPrevPage: boolean
  actionLoadingId: string | null
  actionError: string | null
  selectedOrg: AdminOrgDTO | null
  selectedOrgDocuments: AdminDocumentDTO[]
  isLoadingDocuments: boolean
}>()

const emit = defineEmits<{
  'set-filtro': [estado: string]
  'next-page': []
  'prev-page': []
  'select-org': [org: AdminOrgDTO]
  'clear-selection': []
  approve: [id: string]
  reject: [id: string]
  deactivate: [id: string]
  reactivate: [id: string]
}>()

/** Pills de filtro: clave de estado + etiqueta visible. */
const FILTROS: { key: string; label: string }[] = [
  { key: 'todas', label: 'Todas' },
  { key: 'pendiente', label: 'Pendientes' },
  { key: 'activa', label: 'Activas' },
  { key: 'rechazada', label: 'Rechazadas' },
  { key: 'inactiva', label: 'Inactivas' }
]

/** Etiqueta legible del estado de verificación. */
const ESTADO_LABEL: Record<AdminOrgDTO['estado'], string> = {
  pendiente: 'Pendiente',
  activa: 'Activa',
  rechazada: 'Rechazada',
  inactiva: 'Inactiva'
}

/** Clases del badge de estado (color según verificación). */
const ESTADO_COLOR: Record<AdminOrgDTO['estado'], string> = {
  activa: 'bg-green-100 text-green-700',
  pendiente: 'bg-amber-100 text-amber-700',
  rechazada: 'bg-red-100 text-red-700',
  inactiva: 'bg-slate-100 text-slate-500'
}

/** Etiqueta legible de la función de la organización. */
const TIPO_LABEL: Record<AdminOrgDTO['tipo'], string> = {
  centro_acopio: 'Centro de acopio',
  punto_distribucion: 'Punto de distribución',
  ambos: 'Acopio y distribución'
}

/** Formatea una fecha ISO `YYYY-MM-DD` como `dd/mm/yyyy`. */
function fechaFormateada(fecha: string): string {
  const [y, m, d] = fecha.split('-')
  return `${d}/${m}/${y}`
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6">
    <!-- ===== HEADER ===== -->
    <header class="min-w-0">
      <h1 class="font-display text-2xl font-black uppercase text-navy-800">
        Organizaciones
      </h1>
      <p
        v-if="(conteosPorEstado.pendiente ?? 0) > 0"
        class="mt-1 text-sm font-semibold text-amber-600"
      >
        {{ conteosPorEstado.pendiente ?? 0 }}
        {{ (conteosPorEstado.pendiente ?? 0) === 1 ? 'organización espera' : 'organizaciones esperan' }}
        revisión
      </p>
      <p v-else class="mt-1 text-sm font-semibold text-green-600">
        Todo al día
      </p>
    </header>

    <!-- ===== FILTROS ===== -->
    <div class="mt-5 flex flex-wrap gap-2">
      <button
        v-for="f in FILTROS"
        :key="f.key"
        type="button"
        class="rounded-full px-4 py-1.5 font-display text-xs font-bold uppercase tracking-widest
               transition-colors duration-200"
        :class="filtroEstado === f.key
          ? 'bg-navy-800 text-white'
          : 'bg-white text-navy-600 border border-navy-600/20 hover:bg-navy-800/5'"
        @click="emit('set-filtro', f.key)"
      >
        {{ f.label }} ({{ conteosPorEstado[f.key] ?? 0 }})
      </button>
    </div>

    <!-- ===== ERROR DE CARGA ===== -->
    <p
      v-if="error"
      role="alert"
      class="mt-6 rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
    >
      {{ error }}
    </p>

    <!-- ===== ERROR DE ACCIÓN ===== -->
    <p
      v-if="actionError"
      role="alert"
      class="mt-6 rounded-xl bg-alert/10 px-4 py-3 text-sm font-semibold text-alert"
    >
      {{ actionError }}
    </p>

    <!-- ===== LOADING (skeleton) ===== -->
    <div v-if="isLoading && orgs.length === 0" class="mt-6 flex flex-col gap-3">
      <div
        v-for="n in 4"
        :key="n"
        class="h-16 animate-pulse rounded-xl bg-slate-200"
      />
    </div>

    <!-- ===== VACÍO ===== -->
    <div
      v-else-if="orgs.length === 0"
      class="glass-auth mt-6 rounded-2xl px-4 py-12 text-center"
    >
      <p class="text-sm text-slate-500">No hay organizaciones para este filtro.</p>
    </div>

    <!-- ===== LISTA DE ORGANIZACIONES ===== -->
    <ul v-else class="mt-6 flex flex-col gap-3">
      <li
        v-for="org in orgs"
        :key="org.id"
        class="glass-auth flex flex-col gap-3 rounded-xl p-4 sm:flex-row sm:items-center sm:gap-4"
        :class="actionLoadingId === org.id ? 'pointer-events-none opacity-60' : ''"
      >
        <!-- Nombre + tipo -->
        <div class="min-w-0 flex-1">
          <h2 class="truncate font-display text-base font-bold uppercase text-navy-800">
            {{ org.nombre }}
          </h2>
          <p class="mt-0.5 text-xs text-slate-400">{{ TIPO_LABEL[org.tipo] }}</p>
        </div>

        <!-- Región -->
        <p class="shrink-0 text-sm text-slate-500 sm:w-32">{{ org.region ?? '—' }}</p>

        <!-- Estado badge -->
        <span
          class="shrink-0 self-start rounded-full px-2.5 py-0.5 text-xs font-semibold sm:self-center"
          :class="ESTADO_COLOR[org.estado]"
        >
          {{ ESTADO_LABEL[org.estado] }}
        </span>

        <!-- Acciones según estado -->
        <div class="flex shrink-0 flex-wrap items-center gap-2">
          <!-- Pendiente: aprobar / rechazar -->
          <template v-if="org.estado === 'pendiente'">
            <button
              type="button"
              :disabled="actionLoadingId === org.id"
              class="inline-flex items-center gap-1.5 rounded-lg bg-green-600 px-3 py-1.5 font-display
                     text-xs font-bold uppercase tracking-widest text-white transition-colors
                     hover:bg-green-700 disabled:opacity-50"
              @click="emit('approve', org.id)"
            >
              <svg
                v-if="actionLoadingId === org.id"
                class="h-3.5 w-3.5 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z" />
              </svg>
              Aprobar
            </button>
            <button
              type="button"
              :disabled="actionLoadingId === org.id"
              class="inline-flex items-center gap-1.5 rounded-lg bg-red-600 px-3 py-1.5 font-display
                     text-xs font-bold uppercase tracking-widest text-white transition-colors
                     hover:bg-red-700 disabled:opacity-50"
              @click="emit('reject', org.id)"
            >
              Rechazar
            </button>
            <!-- Abre el drawer para revisar los documentos de respaldo ANTES de
                 aprobar/rechazar (las mismas acciones están dentro del drawer). -->
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-display text-xs
                     font-bold uppercase tracking-widest text-navy-600 transition-colors
                     hover:bg-navy-800/8 hover:text-navy-800"
              @click="emit('select-org', org)"
            >
              Ver detalle
            </button>
          </template>

          <!-- Activa: desactivar + ver detalle -->
          <template v-else-if="org.estado === 'activa'">
            <button
              type="button"
              :disabled="actionLoadingId === org.id"
              class="inline-flex items-center gap-1.5 rounded-lg bg-amber-500 px-3 py-1.5 font-display
                     text-xs font-bold uppercase tracking-widest text-white transition-colors
                     hover:bg-amber-600 disabled:opacity-50"
              @click="emit('deactivate', org.id)"
            >
              <svg
                v-if="actionLoadingId === org.id"
                class="h-3.5 w-3.5 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z" />
              </svg>
              Desactivar
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-display text-xs
                     font-bold uppercase tracking-widest text-navy-600 transition-colors
                     hover:bg-navy-800/8 hover:text-navy-800"
              @click="emit('select-org', org)"
            >
              Ver detalle
            </button>
          </template>

          <!-- Rechazada: solo ver detalle -->
          <template v-else-if="org.estado === 'rechazada'">
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-display text-xs
                     font-bold uppercase tracking-widest text-navy-600 transition-colors
                     hover:bg-navy-800/8 hover:text-navy-800"
              @click="emit('select-org', org)"
            >
              Ver detalle
            </button>
          </template>

          <!-- Inactiva: reactivar + ver detalle -->
          <template v-else>
            <button
              type="button"
              :disabled="actionLoadingId === org.id"
              class="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 font-display
                     text-xs font-bold uppercase tracking-widest text-white transition-colors
                     hover:bg-blue-700 disabled:opacity-50"
              @click="emit('reactivate', org.id)"
            >
              <svg
                v-if="actionLoadingId === org.id"
                class="h-3.5 w-3.5 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z" />
              </svg>
              Reactivar
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-display text-xs
                     font-bold uppercase tracking-widest text-navy-600 transition-colors
                     hover:bg-navy-800/8 hover:text-navy-800"
              @click="emit('select-org', org)"
            >
              Ver detalle
            </button>
          </template>
        </div>
      </li>
    </ul>

    <!-- ===== PAGINADOR ===== -->
    <div
      v-if="orgs.length > 0 && totalPages > 1"
      class="mt-4 flex items-center justify-between gap-3"
    >
      <button
        type="button"
        :disabled="!hasPrevPage"
        class="rounded-lg px-3 py-1.5 font-display text-xs font-bold uppercase tracking-widest
               text-navy-600 transition-colors hover:bg-navy-800/8 disabled:pointer-events-none
               disabled:opacity-40"
        @click="emit('prev-page')"
      >
        ← Anterior
      </button>
      <span class="text-xs font-semibold text-slate-500">
        Página {{ currentPage }} de {{ totalPages }}
      </span>
      <button
        type="button"
        :disabled="!hasNextPage"
        class="rounded-lg px-3 py-1.5 font-display text-xs font-bold uppercase tracking-widest
               text-navy-600 transition-colors hover:bg-navy-800/8 disabled:pointer-events-none
               disabled:opacity-40"
        @click="emit('next-page')"
      >
        Siguiente →
      </button>
    </div>

    <!-- ===== DRAWER DE DETALLE ===== -->
    <template v-if="selectedOrg">
      <!-- Overlay -->
      <div
        class="fixed inset-0 z-40 bg-black/40"
        @click="emit('clear-selection')"
      />

      <!-- Panel -->
      <aside
        class="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col bg-[#f0f4ff] shadow-xl"
        role="dialog"
        aria-label="Detalle de la organización"
      >
        <!-- Header -->
        <header class="flex items-start justify-between gap-3 border-b border-slate-200 px-5 py-4">
          <div class="min-w-0">
            <h2 class="font-display text-xl font-black uppercase leading-tight text-navy-800">
              {{ selectedOrg.nombre }}
            </h2>
            <div class="mt-2 flex flex-wrap items-center gap-2">
              <span class="rounded-full bg-navy-800/8 px-2.5 py-0.5 text-xs font-semibold text-navy-800">
                {{ TIPO_LABEL[selectedOrg.tipo] }}
              </span>
              <span
                class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                :class="ESTADO_COLOR[selectedOrg.estado]"
              >
                {{ ESTADO_LABEL[selectedOrg.estado] }}
              </span>
            </div>
          </div>
          <button
            type="button"
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-slate-400
                   transition-colors hover:bg-navy-800/8 hover:text-navy-800"
            aria-label="Cerrar"
            @click="emit('clear-selection')"
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
        </header>

        <!-- Datos completos -->
        <div class="min-h-0 flex-1 overflow-y-auto px-5 py-4">
          <dl class="flex flex-col gap-3">
            <div>
              <dt class="text-xs uppercase tracking-widest text-slate-400">RUT</dt>
              <dd class="text-sm text-navy-800">{{ selectedOrg.rut ?? '—' }}</dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-widest text-slate-400">Coordinador</dt>
              <dd class="text-sm text-navy-800">{{ selectedOrg.contactoNombre ?? '—' }}</dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-widest text-slate-400">Email</dt>
              <dd class="break-all text-sm text-navy-800">{{ selectedOrg.email }}</dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-widest text-slate-400">Teléfono</dt>
              <dd class="text-sm text-navy-800">{{ selectedOrg.telefono ?? '—' }}</dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-widest text-slate-400">Región</dt>
              <dd class="text-sm text-navy-800">{{ selectedOrg.region ?? '—' }}</dd>
            </div>
            <div>
              <dt class="text-xs uppercase tracking-widest text-slate-400">Fecha de registro</dt>
              <dd class="text-sm text-navy-800">{{ fechaFormateada(selectedOrg.fechaRegistro) }}</dd>
            </div>
            <div v-if="selectedOrg.estado === 'rechazada' && selectedOrg.motivoRechazo">
              <dt class="text-xs uppercase tracking-widest text-red-400">Motivo de rechazo</dt>
              <dd class="mt-0.5 text-sm font-semibold text-red-700">
                {{ selectedOrg.motivoRechazo }}
              </dd>
            </div>
          </dl>

          <!-- Documentos de respaldo -->
          <div class="mt-5 border-t border-slate-200 pt-4">
            <h3 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
              Documentos de respaldo
            </h3>

            <!-- Loading -->
            <div v-if="isLoadingDocuments" class="mt-3 flex flex-col gap-2">
              <div v-for="n in 2" :key="n" class="h-9 animate-pulse rounded-lg bg-slate-200" />
            </div>

            <!-- Vacío -->
            <p
              v-else-if="selectedOrgDocuments.length === 0"
              class="mt-3 text-sm text-slate-400"
            >
              No hay documentos subidos.
            </p>

            <!-- Lista -->
            <ul v-else class="mt-3 flex flex-col gap-2">
              <li
                v-for="doc in selectedOrgDocuments"
                :key="doc.id"
                class="flex items-center gap-2 rounded-lg bg-white/60 px-3 py-2
                       ring-1 ring-navy-800/10"
              >
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
                <span class="min-w-0 flex-1 truncate text-sm text-navy-800">
                  {{ doc.nombreArchivo }}
                </span>
                <span
                  class="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 font-display text-xs
                         font-bold uppercase tracking-widest text-slate-500"
                >
                  {{ doc.tipo }}
                </span>
                <a
                  :href="doc.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="shrink-0 font-display text-xs font-bold uppercase tracking-widest
                         text-navy-600 hover:text-navy-800"
                >
                  Ver
                </a>
              </li>
            </ul>
          </div>

          <!-- Acciones -->
          <div class="mt-6 border-t border-slate-200 pt-4">
            <h3 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
              Acciones
            </h3>
            <div class="mt-3 flex flex-col gap-2">
              <!-- Pendiente -->
              <template v-if="selectedOrg.estado === 'pendiente'">
                <BaseButton
                  variant="navy"
                  size="md"
                  :full-width="true"
                  :disabled="actionLoadingId === selectedOrg.id"
                  class="!bg-green-600 hover:!bg-green-700 !shadow-green-600/25"
                  @click="emit('approve', selectedOrg.id)"
                >
                  {{ actionLoadingId === selectedOrg.id ? 'Procesando…' : 'Aprobar organización' }}
                </BaseButton>
                <BaseButton
                  variant="navy"
                  size="md"
                  :full-width="true"
                  :disabled="actionLoadingId === selectedOrg.id"
                  class="!bg-red-600 hover:!bg-red-700 !shadow-red-600/25"
                  @click="emit('reject', selectedOrg.id)"
                >
                  {{ actionLoadingId === selectedOrg.id ? 'Procesando…' : 'Rechazar organización' }}
                </BaseButton>
              </template>

              <!-- Activa -->
              <template v-else-if="selectedOrg.estado === 'activa'">
                <BaseButton
                  variant="navy"
                  size="md"
                  :full-width="true"
                  :disabled="actionLoadingId === selectedOrg.id"
                  class="!bg-amber-500 hover:!bg-amber-600 !shadow-amber-500/25"
                  @click="emit('deactivate', selectedOrg.id)"
                >
                  {{ actionLoadingId === selectedOrg.id ? 'Procesando…' : 'Desactivar organización' }}
                </BaseButton>
              </template>

              <!-- Inactiva -->
              <template v-else-if="selectedOrg.estado === 'inactiva'">
                <BaseButton
                  variant="navy"
                  size="md"
                  :full-width="true"
                  :disabled="actionLoadingId === selectedOrg.id"
                  class="!bg-blue-600 hover:!bg-blue-700 !shadow-blue-600/25"
                  @click="emit('reactivate', selectedOrg.id)"
                >
                  {{ actionLoadingId === selectedOrg.id ? 'Procesando…' : 'Reactivar organización' }}
                </BaseButton>
              </template>

              <!-- Rechazada: sin acciones disponibles -->
              <p v-else class="text-sm text-slate-400">
                No hay acciones disponibles para una organización rechazada.
              </p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <footer class="border-t border-slate-200 px-5 py-4">
          <BaseButton
            variant="ghost"
            :full-width="true"
            class="border border-navy-600/25"
            @click="emit('clear-selection')"
          >
            Cerrar
          </BaseButton>
        </footer>
      </aside>
    </template>
  </div>
</template>
