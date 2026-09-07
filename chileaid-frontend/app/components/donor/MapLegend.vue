<script setup lang="ts">
import { ref } from 'vue'
import { COBERTURA_LEGEND } from '~/utils/cobertura'
import { TIPOS_CENTRO, labelTipoCentro, colorTipoCentro } from '~/utils/tipoCentro'

/**
 * VIEW — Leyenda/simbología del mapa. Puramente visual: no recibe datos de
 * dominio ni conoce servicios/composables; solo lee los diccionarios de
 * presentación (colores de cobertura y tipos de centro) para explicar qué
 * significa cada elemento del mapa. Colapsable en mobile (siempre visible en
 * desktop).
 */
const open = ref(false)
</script>

<template>
  <div class="absolute bottom-4 left-4 z-[1000] w-56 max-w-[calc(100%-2rem)]">
    <div class="glass-auth rounded-2xl shadow-xl">
      <button
        type="button"
        class="flex w-full items-center justify-between gap-2 px-4 py-2.5"
        :aria-expanded="open"
        @click="open = !open"
      >
        <span class="font-display text-xs font-bold uppercase tracking-widest text-navy-600">
          Simbología
        </span>
        <svg
          class="h-4 w-4 text-navy-600 transition-transform lg:hidden"
          :class="open ? 'rotate-180' : ''"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      <div class="px-4 pb-4" :class="open ? 'block' : 'hidden lg:block'">
        <!-- Color del pin según cobertura (lo que el usuario lee en el mapa) -->
        <p class="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
          Estado del centro
        </p>
        <ul class="space-y-1.5">
          <li
            v-for="item in COBERTURA_LEGEND"
            :key="item.label"
            class="flex items-start gap-2"
          >
            <span
              class="mt-0.5 h-3.5 w-3.5 shrink-0 rounded-full border-2 border-white shadow"
              :style="{ background: item.color }"
            />
            <span class="text-xs leading-snug text-navy-800">
              <span class="font-semibold">{{ item.label }}</span>
              <span class="text-slate-500"> — {{ item.hint }}</span>
            </span>
          </li>
        </ul>
        <p class="mt-2 flex items-center gap-2 text-xs text-slate-500">
          <span
            class="alert-pulse h-3.5 w-3.5 shrink-0 rounded-full border-2 border-white shadow"
            style="background: #dc2626"
          />
          El punto late = crítico
        </p>

        <!-- Tipo de centro (badge del panel al abrir un centro) -->
        <p class="mb-1.5 mt-4 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
          Tipo de centro
        </p>
        <ul class="flex flex-wrap gap-1.5">
          <li v-for="tipo in TIPOS_CENTRO" :key="tipo">
            <span
              class="inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold"
              :class="colorTipoCentro(tipo)"
            >
              {{ labelTipoCentro(tipo) }}
            </span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
