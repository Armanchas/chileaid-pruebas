<script setup lang="ts">
/**
 * PÁGINA — Panel de inicio del administrador. Orquesta el ViewModel y reparte
 * estado/acciones a la vista vía props/eventos. Cero lógica de negocio.
 */
import { useAdminDashboardViewModel } from '~/composables/useAdminDashboardViewModel'
import AdminDashboardView from '~/components/admin/AdminDashboardView.vue'

definePageMeta({ layout: 'admin', middleware: 'auth-admin' })

const {
  stats,
  recentActivity,
  isLoading,
  error,
  tasaPendientes,
  actividadLabel,
  actividadColor,
  loadDashboard,
  goOrgs,
  goCatalog
} = useAdminDashboardViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadDashboard()
</script>

<template>
  <AdminDashboardView
    :stats="stats"
    :recent-activity="recentActivity"
    :is-loading="isLoading"
    :error="error"
    :tasa-pendientes="tasaPendientes"
    :actividad-label="actividadLabel"
    :actividad-color="actividadColor"
    @go-orgs="goOrgs"
    @go-catalog="goCatalog"
  />
</template>
