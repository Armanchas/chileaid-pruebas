<script setup lang="ts">
/**
 * Sección de documentos de respaldo de la organización (RF-03).
 *
 * Es una sección autónoma: incluye su propio ViewModel para no arrastrar
 * estado de documentos a través del árbol de perfil. Carga los documentos
 * al montarse y permite subir nuevos archivos (PDF o JPG) mediante un flujo
 * de subida directa a S3 con presigned POST.
 */
import { onMounted, useTemplateRef } from 'vue'
import { useOrgDocumentsViewModel } from '~/composables/useOrgDocumentsViewModel'

const {
  documents,
  isLoading,
  error,
  isUploading,
  uploadError,
  uploadSuccess,
  loadDocuments,
  uploadDocument
} = useOrgDocumentsViewModel()

const fileInput = useTemplateRef<HTMLInputElement>('fileInput')

onMounted(loadDocuments)

function onFileChange(event: Event): void {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadDocument(file).then(() => {
    if (fileInput.value) fileInput.value.value = ''
  })
}
</script>

<template>
  <section class="glass-auth rounded-2xl p-5 sm:p-6">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h2 class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
          Documentos de respaldo
        </h2>
        <p class="mt-1 text-sm text-slate-500">
          PDF o JPG — máx. un archivo por subida
        </p>
      </div>

      <!-- Botón de subida -->
      <label
        class="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-navy-800 px-4 py-2
               font-display text-xs font-bold uppercase tracking-widest text-white
               transition-colors hover:bg-navy-700 disabled:opacity-50"
        :class="isUploading ? 'pointer-events-none opacity-60' : ''"
      >
        <svg
          v-if="isUploading"
          class="h-3.5 w-3.5 animate-spin"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z" />
        </svg>
        <svg
          v-else
          class="h-3.5 w-3.5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        {{ isUploading ? 'Subiendo…' : 'Subir documento' }}
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.jpg,.jpeg"
          class="sr-only"
          :disabled="isUploading"
          @change="onFileChange"
        >
      </label>
    </div>

    <!-- Feedback de subida -->
    <p
      v-if="uploadSuccess"
      class="mt-4 rounded-lg bg-green-50 px-4 py-2.5 text-sm font-semibold text-green-700
             ring-1 ring-green-600/30"
    >
      Documento subido correctamente.
    </p>
    <p
      v-else-if="uploadError"
      role="alert"
      class="mt-4 rounded-lg bg-alert/10 px-4 py-2.5 text-sm font-semibold text-alert
             ring-1 ring-alert/30"
    >
      {{ uploadError }}
    </p>

    <!-- Error de carga -->
    <p
      v-if="error"
      role="alert"
      class="mt-4 rounded-lg bg-alert/10 px-4 py-2.5 text-sm font-semibold text-alert"
    >
      {{ error }}
    </p>

    <!-- Loading skeleton -->
    <div v-else-if="isLoading" class="mt-4 flex flex-col gap-2">
      <div v-for="n in 2" :key="n" class="h-10 animate-pulse rounded-lg bg-slate-200" />
    </div>

    <!-- Vacío -->
    <p
      v-else-if="documents.length === 0"
      class="mt-4 text-sm text-slate-400"
    >
      No hay documentos subidos todavía. Sube al menos uno para que el equipo de
      Chile Aid pueda validar tu organización.
    </p>

    <!-- Lista de documentos -->
    <ul v-else class="mt-4 flex flex-col gap-2">
      <li
        v-for="doc in documents"
        :key="doc.id"
        class="flex items-center gap-3 rounded-lg bg-white/60 px-4 py-2.5 ring-1 ring-navy-800/10"
      >
        <!-- Ícono según tipo -->
        <svg
          class="h-4 w-4 shrink-0 text-slate-400"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
          <path d="M14 2v6h6" />
        </svg>

        <span class="min-w-0 flex-1 truncate text-sm text-navy-800">
          {{ doc.nombreArchivo }}
        </span>

        <span
          class="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 font-display text-xs
                 font-bold uppercase tracking-widest text-slate-500"
        >
          {{ doc.tipo }}
        </span>

        <a
          :href="doc.url"
          target="_blank"
          rel="noopener noreferrer"
          class="shrink-0 font-display text-xs font-bold uppercase tracking-widest
                 text-navy-600 hover:text-navy-800"
        >
          Ver
        </a>
      </li>
    </ul>
  </section>
</template>
