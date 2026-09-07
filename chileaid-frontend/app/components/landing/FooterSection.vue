<script setup lang="ts">
import type { EmergencyNumber } from '~/services/statsService'

/**
 * VIEW — Footer institucional: logo, números de emergencia de Chile,
 * links y copyright. Recibe los números por props.
 */
defineProps<{ emergencyNumbers: EmergencyNumber[] }>()

const year = new Date().getFullYear()

const institutionalLinks = [
  'Sobre Chile Aid',
  'Organizaciones verificadas',
  'Transparencia',
  'Preguntas frecuentes',
  'Contacto'
]
</script>

<template>
  <footer class="bg-navy-900 text-white">
    <div class="mx-auto grid max-w-7xl gap-10 px-4 py-14 sm:px-6 lg:grid-cols-3 lg:px-8">
      <!-- Marca -->
      <div>
        <div class="flex items-center gap-2.5">
          <span
            class="flex h-9 w-9 items-center justify-center rounded-md bg-white text-navy-800
                   font-display text-xl font-black"
            aria-hidden="true"
          >+</span>
          <span class="font-display text-2xl font-black uppercase tracking-tight">
            Chile<span class="text-alert-500">Aid</span>
          </span>
        </div>
        <p class="mt-4 max-w-xs text-sm text-white/60">
          Coordinación civil de donaciones humanitarias para emergencias en Chile:
          terremotos, incendios y aluviones.
        </p>
      </div>

      <!-- Números de emergencia -->
      <div>
        <h3 class="font-display text-sm font-bold uppercase tracking-widest text-white/50">
          Números de emergencia
        </h3>
        <ul class="mt-4 space-y-2">
          <li
            v-for="item in emergencyNumbers"
            :key="item.id"
            class="flex items-center justify-between border-b border-white/10 pb-2"
          >
            <span class="text-white/75">{{ item.name }}</span>
            <a
              :href="`tel:${item.number}`"
              class="font-display text-2xl font-black text-alert-500 transition hover:text-white"
            >{{ item.number }}</a>
          </li>
        </ul>
      </div>

      <!-- Links institucionales -->
      <div>
        <h3 class="font-display text-sm font-bold uppercase tracking-widest text-white/50">
          Institucional
        </h3>
        <ul class="mt-4 space-y-2.5">
          <li v-for="link in institutionalLinks" :key="link">
            <a href="#" class="text-sm text-white/70 transition hover:text-white">{{ link }}</a>
          </li>
        </ul>
      </div>
    </div>

    <div class="border-t border-white/10">
      <div
        class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-4 py-5
               text-sm text-white/50 sm:flex-row sm:px-6 lg:px-8"
      >
        <p>© {{ year }} Chile Aid. Plataforma sin fines de lucro.</p>
        <p>Hecho en Chile 🇨🇱 para responder juntos.</p>
      </div>
    </div>
  </footer>
</template>
