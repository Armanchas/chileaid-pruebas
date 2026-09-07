<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import type { StatItem } from '~/services/statsService'
import StatCard from '~/components/ui/StatCard.vue'

/**
 * VIEW — Banda de estadísticas sobre fondo azul profundo. Recibe `stats` por
 * props. La animación de entrada escalonada se dispara al entrar en viewport
 * (lógica puramente visual: presentación, no datos).
 */
defineProps<{ stats: StatItem[] }>()

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)
let observer: IntersectionObserver | null = null

onMounted(() => {
  if (!sectionRef.value) return
  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry?.isIntersecting) {
        visible.value = true
        observer?.disconnect()
      }
    },
    { threshold: 0.3 }
  )
  observer.observe(sectionRef.value)
})

onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <section
    ref="sectionRef"
    class="relative bg-gradient-to-b from-navy-800 to-navy-900 py-20 sm:py-24"
  >
    <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
      <p
        class="text-center font-display text-sm font-bold uppercase tracking-[0.25em] text-white/50"
      >
        Operación nacional en tiempo real
      </p>

      <div class="mt-12 grid gap-12 sm:grid-cols-3 sm:gap-8">
        <StatCard
          v-for="(stat, i) in stats"
          :key="stat.id"
          :display="stat.display"
          :label="stat.label"
          :visible="visible"
          :delay="i * 180"
        />
      </div>
    </div>
  </section>
</template>
