<script setup lang="ts">
import type { HowItWorksCard } from '~/services/statsService'
import BaseButton from '~/components/ui/BaseButton.vue'

/**
 * VIEW — "Cómo funciona": dos tarjetas (ciudadanos / organizaciones) con
 * hover de elevación. Recibe las tarjetas por props y emite la intención
 * de cada CTA hacia arriba.
 */
defineProps<{ cards: HowItWorksCard[] }>()
defineEmits<{ select: [id: string] }>()
</script>

<template>
  <section id="como-funciona" class="bg-surface py-20 sm:py-28">
    <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-2xl text-center">
        <h2 class="font-display text-4xl font-black uppercase text-navy-800 sm:text-5xl">
          Cómo funciona
        </h2>
        <p class="mt-4 text-lg text-gray-600">
          Una sola plataforma, dos caminos. La ayuda llega coordinada y verificada.
        </p>
      </div>

      <div class="mt-14 grid gap-6 md:grid-cols-2">
        <article
          v-for="card in cards"
          :key="card.id"
          class="group flex flex-col rounded-2xl border border-gray-200 bg-white p-8
                 shadow-sm transition-all duration-300 ease-out
                 hover:-translate-y-2 hover:shadow-2xl"
          :class="card.accent === 'alert'
            ? 'hover:border-alert/40 hover:shadow-alert/10'
            : 'hover:border-navy-600/40 hover:shadow-navy-600/10'"
        >
          <span
            class="inline-flex w-fit items-center rounded-full px-3 py-1 font-display text-xs
                   font-bold uppercase tracking-widest"
            :class="card.accent === 'alert'
              ? 'bg-alert/10 text-alert'
              : 'bg-navy-600/10 text-navy-600'"
          >
            {{ card.audience }}
          </span>

          <h3 class="mt-5 font-display text-3xl font-black uppercase text-navy-800">
            {{ card.title }}
          </h3>
          <p class="mt-3 text-gray-600">
            {{ card.description }}
          </p>

          <ol class="mt-6 space-y-3">
            <li
              v-for="(step, i) in card.steps"
              :key="i"
              class="flex gap-3 text-gray-700"
            >
              <span
                class="grid h-6 w-6 shrink-0 place-items-center rounded-full font-display
                       text-sm font-bold text-white"
                :class="card.accent === 'alert' ? 'bg-alert' : 'bg-navy-600'"
              >{{ i + 1 }}</span>
              <span>{{ step }}</span>
            </li>
          </ol>

          <div class="mt-8 pt-2">
            <BaseButton
              :variant="card.accent === 'alert' ? 'primary' : 'ghost'"
              full-width
              @click="$emit('select', card.id)"
            >
              {{ card.cta }}
            </BaseButton>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
