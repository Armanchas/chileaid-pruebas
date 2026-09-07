<script setup lang="ts">
/**
 * LAYOUT — Base para todas las páginas del panel de administración. Monta la
 * navbar reutilizable y deja el contenido en el <slot />. Sin lógica de negocio.
 *
 * La navbar es fija (superior en desktop, inferior en mobile), por eso el
 * contenido reserva padding-top en desktop y padding-bottom en mobile para no
 * quedar tapado.
 */
import AdminNavbar from '~/components/admin/AdminNavbar.vue'
</script>

<template>
  <div class="min-h-screen bg-[#f0f4ff] pb-20 pt-0 md:pb-0 md:pt-14">
    <AdminNavbar />
    <slot />
  </div>
</template>
