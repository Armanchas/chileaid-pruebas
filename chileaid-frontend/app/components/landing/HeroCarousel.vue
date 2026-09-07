<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

/**
 * VIEW — Carrusel de fondo del hero. Recibe las imágenes por props (no llama
 * servicios) y rota entre ellas automáticamente con transición fade. Cada
 * imagen lleva un overlay oscuro para mantener legible el contenido encima.
 */
const props = withDefaults(
  defineProps<{ images: string[]; interval?: number }>(),
  { interval: 5000 }
)

const activeIndex = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function next(): void {
  if (props.images.length <= 1) return
  activeIndex.value = (activeIndex.value + 1) % props.images.length
}

onMounted(() => {
  // Respeta a quienes prefieren menos movimiento: sin auto-rotación.
  const reduced =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduced || props.images.length <= 1) return
  timer = setInterval(next, props.interval)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="pointer-events-none absolute inset-0 overflow-hidden">
    <div
      v-for="(src, i) in images"
      :key="src"
      class="absolute inset-0 bg-cover bg-center transition-opacity duration-1000 ease-in-out"
      :class="i === activeIndex ? 'opacity-100' : 'opacity-0'"
      :style="{ backgroundImage: `url(${src})` }"
      :aria-hidden="i === activeIndex ? 'false' : 'true'"
    />
    <!-- Overlay oscuro para legibilidad del texto del hero -->
    <div class="absolute inset-0" style="background: rgba(10, 20, 50, 0.6);" />
  </div>
</template>
