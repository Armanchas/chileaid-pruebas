<script setup lang="ts">
/**
 * PÁGINA — Detalle de un centro de acopio. Solo orquesta: toma el ViewModel,
 * carga el centro de la ruta y reparte estado/acciones a la vista vía
 * props/eventos. Sin lógica de negocio ni datos.
 */
import { useCenterDetailViewModel } from '~/composables/useCenterDetailViewModel'
import CenterDetailView from '~/components/donor/center/CenterDetailView.vue'

definePageMeta({ layout: 'donor', middleware: 'auth-donor' })

const route = useRoute()
const id = route.params.id as string

const { center, isLoading, error, loadCenter } = useCenterDetailViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadCenter(id)
</script>

<template>
  <CenterDetailView
    :center="center"
    :is-loading="isLoading"
    :error="error"
    @go-back="() => navigateTo('/donor/centers')"
    @donate="() => navigateTo('/donor/donate/' + id)"
    @open-map="() => navigateTo({ path: '/donor/map', query: { center: id } })"
  />
</template>
