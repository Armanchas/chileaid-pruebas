<script setup lang="ts">
/**
 * VIEW — Información operativa del centro (contacto + ubicación).
 * Puramente visual: recibe datos por props y emite `open-map`.
 */
defineProps<{
  coordinador: string
  telefono: string
}>()

const emit = defineEmits<{
  'open-map': []
}>()
</script>

<template>
  <section class="glass-auth rounded-2xl p-6">
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
      <!-- Columna 1: contacto -->
      <div>
        <h3 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Información de contacto
        </h3>
        <div class="mt-3 space-y-2 text-navy-700">
          <p class="flex items-center gap-2">
            <svg
              class="h-4 w-4 shrink-0 text-navy-600"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="8" r="3.5" />
              <path d="M5 20a7 7 0 0 1 14 0" />
            </svg>
            {{ coordinador }}
          </p>
          <p class="flex items-center gap-2">
            <svg
              class="h-4 w-4 shrink-0 text-navy-600"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L20 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 5 6a2 2 0 0 1 0-2z" />
            </svg>
            <a :href="`tel:${telefono.replace(/\s+/g, '')}`" class="hover:underline">
              {{ telefono }}
            </a>
          </p>
        </div>
      </div>

      <!-- Columna 2: ubicación -->
      <div>
        <h3 class="flex items-center gap-2 font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          <svg
            class="h-4 w-4 shrink-0 text-navy-600"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="M3 6h11v9H3z" />
            <path d="M14 9h4l3 3v3h-7z" />
            <circle cx="7" cy="18" r="1.5" />
            <circle cx="17" cy="18" r="1.5" />
          </svg>
          Cómo llegar
        </h3>
        <p class="mt-3 text-slate-500">
          Ubica el centro en el mapa para planificar tu entrega.
        </p>
        <button
          type="button"
          class="mt-4 inline-flex items-center gap-2 rounded-lg border border-navy-600/25
                 px-4 py-2 font-display text-sm font-bold uppercase tracking-wide text-navy-600
                 transition-colors duration-200 hover:bg-navy-800/5
                 focus:outline-none focus-visible:ring-4 focus-visible:ring-navy-600/20"
          @click="emit('open-map')"
        >
          Ver en mapa
        </button>
      </div>
    </div>
  </section>
</template>
