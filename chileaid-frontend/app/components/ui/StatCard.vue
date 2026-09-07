<script setup lang="ts">
/**
 * VIEW (UI) — Tarjeta de estadística. Muestra un número display enorme y su
 * etiqueta. Recibe el `delay` para la entrada escalonada y `visible` para
 * disparar la animación. Sin lógica de datos.
 */
interface Props {
  display: string
  label: string
  /** Retardo de entrada en ms (escalonado) */
  delay?: number
  /** La vista controla cuándo se vuelve visible */
  visible?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  delay: 0,
  visible: true
})
</script>

<template>
  <div
    class="fade-rise text-center"
    :class="{ 'is-visible': props.visible }"
    :style="{ animationDelay: `${props.delay}ms` }"
  >
    <p
      class="font-display font-black leading-none text-white tabular-nums
             text-6xl sm:text-7xl lg:text-8xl"
    >
      {{ props.display }}
    </p>
    <p
      class="mt-3 font-display font-semibold uppercase tracking-[0.15em]
             text-sm sm:text-base text-white/70"
    >
      {{ props.label }}
    </p>
  </div>
</template>
