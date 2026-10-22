<script setup lang="ts">
import type { HeroContent, StatItem } from '~/services/statsService'
import BaseButton from '~/components/ui/BaseButton.vue'
import HeroCarousel from '~/components/landing/HeroCarousel.vue'

/**
 * VIEW — Hero con carrusel de fotografías de fondo y panel glassmorphic.
 * Recibe el contenido, las imágenes y las métricas por props; emite las
 * intenciones de CTA. El panel "Estado de la red" refleja `stats` (datos reales
 * del backend, `GET /stats`), nunca valores hardcodeados.
 */
defineProps<{ content: HeroContent | null; images: string[]; stats: StatItem[] }>()
defineEmits<{ donate: []; registerCenter: []; viewMap: [] }>()
</script>

<template>
  <section
    id="top"
    class="relative flex min-h-screen items-center overflow-hidden bg-navy-900"
  >
    <!-- Carrusel de fotografías de fondo (con overlay oscuro incluido) -->
    <HeroCarousel :images="images" />

    <div class="relative mx-auto grid w-full max-w-7xl gap-12 px-4 pb-16 pt-28 sm:px-6
                lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:gap-8 lg:px-8 lg:pt-24">
      <!-- Columna de mensaje -->
      <div v-if="content" class="max-w-2xl">
        <span
          class="alert-pulse inline-flex items-center gap-2 rounded-full bg-alert px-4 py-1.5
                 font-display text-sm font-bold uppercase tracking-widest text-white"
        >
          <span class="h-2 w-2 rounded-full bg-white" />
          {{ content.badge }}
        </span>

        <h1
          class="mt-6 font-display text-5xl font-black uppercase text-white
                 sm:text-6xl lg:text-7xl"
        >
          {{ content.title }}
        </h1>

        <p class="mt-6 max-w-xl text-lg text-white/75 sm:text-xl">
          {{ content.subtitle }}
        </p>

        <div class="mt-9 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <BaseButton variant="primary" size="lg" @click="$emit('viewMap')">
            Ver mapa de centros
          </BaseButton>
          <BaseButton variant="secondary" size="lg" @click="$emit('donate')">
            {{ content.primaryCta }}
          </BaseButton>
          <BaseButton variant="secondary" size="lg" @click="$emit('registerCenter')">
            {{ content.secondaryCta }}
          </BaseButton>
        </div>
      </div>

      <!-- Panel glassmorphic — estado de la operación -->
      <div class="glass rounded-2xl p-6 shadow-2xl sm:p-8">
        <div class="flex items-center justify-between border-b border-white/15 pb-4">
          <p class="font-display text-sm font-bold uppercase tracking-widest text-white/60">
            Estado de la red
          </p>
          <span class="flex items-center gap-2 text-sm font-semibold text-emerald-300">
            <span class="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            En línea
          </span>
        </div>

        <ul v-if="stats.length" class="mt-5 space-y-4">
          <li
            v-for="stat in stats"
            :key="stat.id"
            class="flex items-center justify-between gap-4"
          >
            <span class="text-white/70">{{ stat.label }}</span>
            <span class="font-display text-2xl font-black text-white">{{ stat.display }}</span>
          </li>
        </ul>

        <!-- Skeleton mientras cargan las métricas (SSR/latencia) -->
        <ul v-else class="mt-5 space-y-4">
          <li
            v-for="n in 4"
            :key="n"
            class="h-7 animate-pulse rounded bg-white/10"
          />
        </ul>
      </div>
    </div>
  </section>
</template>
