<script setup lang="ts">
import type { TutorialTrack } from '~/services/statsService'
import BaseButton from '~/components/ui/BaseButton.vue'

/**
 * VIEW — Tutorial visual "cómo funciona": dos carriles (cómo donar / cómo
 * solicitar) como un paso a paso con íconos numerados. Recibe los carriles por
 * props y emite la intención del CTA hacia arriba. Puramente visual: no conoce
 * servicios ni composables.
 *
 * El copy y el orden de los pasos vienen del backend (`GET /content/tutorial`);
 * aquí solo se resuelve la clave `icon` de cada paso a un SVG inline (presentación).
 */
defineProps<{ tracks: TutorialTrack[] }>()
defineEmits<{ select: [id: string] }>()

/**
 * Paths SVG por clave de ícono (24x24, stroke currentColor). Se mantienen aquí,
 * en la capa de presentación, porque son decisión de UI, no dato de dominio.
 */
const iconPaths: Record<string, string[]> = {
  search: ['M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z', 'm21 21-4.35-4.35'],
  pin: [
    'M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z',
    'M12 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z'
  ],
  gift: [
    'M20 12v9H4v-9',
    'M2 7h20v5H2z',
    'M12 22V7',
    'M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z',
    'M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z'
  ],
  route: ['M22 12h-4l-3 9L9 3l-3 9H2'],
  shield: ['M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z', 'm9 12 2 2 4-4'],
  clipboard: [
    'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2',
    'M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2z',
    'M9 12h6',
    'M9 16h4'
  ],
  inbox: [
    'M22 12h-6l-2 3h-4l-2-3H2',
    'M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z'
  ]
}

/** Fallback: un círculo neutro si la clave de ícono no está mapeada. */
function pathsFor(icon: string): string[] {
  return iconPaths[icon] ?? ['M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z']
}
</script>

<template>
  <section id="como-funciona" class="bg-surface py-20 sm:py-28">
    <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-2xl text-center">
        <h2 class="font-display text-4xl font-black uppercase text-navy-800 sm:text-5xl">
          Cómo funciona
        </h2>
        <p class="mt-4 text-lg text-gray-600">
          Dos caminos, una sola plataforma. Sigue los pasos para donar o para
          solicitar ayuda.
        </p>
      </div>

      <div class="mt-14 space-y-10">
        <article
          v-for="track in tracks"
          :key="track.id"
          class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8"
        >
          <!-- Encabezado del carril -->
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <span
                class="inline-flex w-fit items-center rounded-full px-3 py-1 font-display
                       text-xs font-bold uppercase tracking-widest"
                :class="track.accent === 'alert'
                  ? 'bg-alert/10 text-alert'
                  : 'bg-navy-600/10 text-navy-600'"
              >
                {{ track.audience }}
              </span>
              <h3 class="mt-3 font-display text-3xl font-black uppercase text-navy-800">
                {{ track.title }}
              </h3>
            </div>
          </div>

          <!-- Pasos: apilados en mobile, en fila con conector en desktop -->
          <ol
            class="mt-8 grid grid-cols-1 gap-8"
            :class="track.steps.length === 4 ? 'lg:grid-cols-4' : 'lg:grid-cols-3'"
          >
            <li
              v-for="(step, i) in track.steps"
              :key="i"
              class="relative flex flex-col items-center text-center"
            >
              <!-- Conector horizontal hacia el siguiente paso (solo desktop) -->
              <span
                v-if="i < track.steps.length - 1"
                class="absolute left-1/2 top-8 hidden h-px w-[calc(100%+2rem)] bg-gray-200 lg:block"
                aria-hidden="true"
              />

              <!-- Círculo con ícono + número de paso -->
              <div
                class="relative z-10 grid h-16 w-16 place-items-center rounded-2xl"
                :class="track.accent === 'alert'
                  ? 'bg-alert/10 text-alert'
                  : 'bg-navy-600/10 text-navy-600'"
              >
                <svg
                  class="h-7 w-7"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.75"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path v-for="(d, k) in pathsFor(step.icon)" :key="k" :d="d" />
                </svg>
                <span
                  class="absolute -right-1.5 -top-1.5 grid h-6 w-6 place-items-center rounded-full
                         font-display text-xs font-bold text-white"
                  :class="track.accent === 'alert' ? 'bg-alert' : 'bg-navy-600'"
                >
                  {{ i + 1 }}
                </span>
              </div>

              <h4 class="mt-4 font-display text-lg font-black uppercase text-navy-800">
                {{ step.title }}
              </h4>
              <p class="mt-2 text-sm text-gray-600">
                {{ step.description }}
              </p>
            </li>
          </ol>

          <div class="mt-8 sm:mx-auto sm:max-w-xs">
            <BaseButton
              :variant="track.accent === 'alert' ? 'primary' : 'ghost'"
              full-width
              @click="$emit('select', track.id)"
            >
              {{ track.cta }}
            </BaseButton>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
