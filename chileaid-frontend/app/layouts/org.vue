<script setup lang="ts">
/**
 * LAYOUT — Base para todas las páginas de la organización receptora. Monta la
 * navbar reutilizable y deja el contenido en el <slot />. Sin lógica de negocio.
 *
 * La navbar es fija (superior en desktop, inferior en mobile), por eso el
 * contenido reserva padding-top en desktop y padding-bottom en mobile para no
 * quedar tapado.
 */
import OrgNavbar from '~/components/org/OrgNavbar.vue'
</script>

<template>
  <div class="min-h-screen bg-[#f0f4ff] pb-20 pt-0 md:pb-0 md:pt-14">
    <OrgNavbar />
    <slot />
  </div>
</template>
