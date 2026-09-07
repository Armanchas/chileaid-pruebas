<script setup lang="ts">
/**
 * VIEW — Header fijo con glassmorphism. Logo + accesos rápidos.
 * Emite intenciones hacia arriba; no contiene lógica de datos.
 */
defineEmits<{ donate: []; emergency: []; account: [] }>()
</script>

<template>
  <header
    class="glass-light fixed inset-x-0 top-0 z-50"
  >
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <!-- Logo -->
      <a href="#top" class="flex items-center gap-2.5 select-none">
        <span
          class="flex h-9 w-9 items-center justify-center rounded-md bg-navy-800 text-white shadow-md"
          aria-hidden="true"
        >
          <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
            <path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3z" />
          </svg>
        </span>
        <span class="font-display text-2xl font-black uppercase tracking-tight text-navy-800">
          Chile<span class="text-alert">Aid</span>
        </span>
      </a>

      <!-- Accesos rápidos -->
      <div class="flex items-center gap-1.5 sm:gap-3">
        <button
          type="button"
          class="alert-pulse hidden items-center gap-2 rounded-lg bg-alert px-4 py-2
                 font-display font-bold uppercase tracking-wide text-white
                 transition hover:bg-alert-600 sm:inline-flex"
          @click="$emit('emergency')"
        >
          <span class="h-2 w-2 animate-ping rounded-full bg-white" />
          Emergencia
        </button>

        <button
          type="button"
          class="grid h-10 w-10 place-items-center rounded-lg bg-navy-800/10
                 transition hover:bg-navy-800/20"
          aria-label="Mi cuenta — iniciar sesión"
          @click="$emit('account')"
        >
          <!-- Avatar minimalista: círculo con silueta de persona -->
          <svg viewBox="0 0 24 24" class="h-7 w-7" aria-hidden="true">
            <circle cx="12" cy="12" r="11" fill="#002675" />
            <circle cx="12" cy="9.5" r="3.4" fill="#ffffff" />
            <path d="M5.5 19a6.5 6.5 0 0113 0z" fill="#ffffff" />
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>
