<script setup lang="ts">
import BaseButton from '~/components/ui/BaseButton.vue'

/**
 * VIEW — Formulario de registro de organización receptora (CU-01), estética
 * "Opción 1" sobre fondo claro. Una sola página con cuatro secciones de datos
 * (no son pasos) — datos de la organización · datos de contacto ·
 * credenciales · documentación — esta última con el adjunto real del
 * documento de respaldo (PDF/JPG), obligatorio para completar el alta.
 *
 * Puramente visual: recibe el modelo compuesto, los errores y los flags
 * `touched` ya resueltos por el ViewModel, y comunica intenciones por eventos.
 * No conoce servicios ni composables; los tipos del modelo se declaran aquí de
 * forma local para no acoplar la vista a la capa de datos.
 */

/** Forma del modelo editable (el `<select>` de función admite '' = sin elegir). */
interface OrgFormModel {
  nombre: string
  tipoCentro: string
  rut?: string
  region: string
  direccion: string
  contactoNombre: string
  email: string
  telefono: string
  password: string
  confirmPassword: string
}

const props = defineProps<{
  modelValue: OrgFormModel
  documentFile: File | null
  errors: Record<string, string | null>
  touched: Record<string, boolean>
  isLoading: boolean
  submitError: string | null
  isFormValid: boolean
  regiones: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [payload: { field: string; value: string }]
  'document-change': [file: File | null]
  submit: []
  'field-touch': [field: string]
}>()

/** Emite el cambio de un único campo (v-model compuesto, campo a campo). */
function update(field: string, value: string): void {
  emit('update:modelValue', { field, value })
}

function onDocumentInput(event: Event): void {
  const input = event.target as HTMLInputElement
  emit('document-change', input.files?.[0] ?? null)
}

function onSubmit(): void {
  if (!props.isFormValid || props.isLoading) return
  emit('submit')
}

/** Clases base compartidas por inputs, selects y textareas. */
const fieldBase =
  'w-full rounded-lg bg-white px-3 py-2.5 text-navy-900 placeholder-slate-400 ' +
  'transition-shadow duration-200 focus:outline-none'

/** Ring del campo: navy por defecto, alert si tiene error visible. */
function fieldRing(field: string): string {
  return props.errors[field]
    ? 'ring-1 ring-alert focus:ring-2 focus:ring-alert'
    : 'ring-1 ring-navy-600/20 focus:ring-2 focus:ring-navy-600'
}
</script>

<template>
  <form
    class="glass-auth w-full max-w-2xl rounded-2xl p-6 sm:p-8"
    novalidate
    @submit.prevent="onSubmit"
  >
    <!-- ===== SECCIÓN 1 — Datos de la organización ===== -->
    <fieldset class="space-y-5">
      <legend class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
        Datos de la organización
      </legend>

      <!-- Nombre -->
      <div>
        <label for="org-nombre" class="block text-sm font-medium text-navy-800">
          Nombre de la organización *
        </label>
        <input
          id="org-nombre"
          :value="modelValue.nombre"
          type="text"
          autocomplete="organization"
          placeholder="Ej: Fundación Manos Unidas"
          :aria-invalid="!!errors.nombre"
          :class="['mt-1', fieldBase, fieldRing('nombre')]"
          @input="update('nombre', ($event.target as HTMLInputElement).value)"
          @blur="emit('field-touch', 'nombre')"
        >
        <p v-if="errors.nombre" class="mt-1 text-xs text-alert">
          {{ errors.nombre }}
        </p>
      </div>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <!-- Función (tipo de centro) -->
        <div>
          <label for="org-tipo-centro" class="block text-sm font-medium text-navy-800">
            Función *
          </label>
          <select
            id="org-tipo-centro"
            :value="modelValue.tipoCentro"
            :aria-invalid="!!errors.tipoCentro"
            :class="[
              'mt-1',
              fieldBase,
              fieldRing('tipoCentro'),
              modelValue.tipoCentro === '' ? 'text-slate-400' : ''
            ]"
            @change="update('tipoCentro', ($event.target as HTMLSelectElement).value)"
            @blur="emit('field-touch', 'tipoCentro')"
          >
            <option value="" disabled>¿Qué función cumple?</option>
            <option value="centro_acopio">Centro de acopio</option>
            <option value="punto_distribucion">Punto de distribución</option>
            <option value="ambos">Ambos</option>
          </select>
          <p v-if="errors.tipoCentro" class="mt-1 text-xs text-alert">
            {{ errors.tipoCentro }}
          </p>
        </div>

        <!-- RUT (opcional) -->
        <div>
          <label for="org-rut" class="block text-sm font-medium text-navy-800">
            RUT
            <span class="font-normal text-slate-500">(opcional)</span>
          </label>
          <input
            id="org-rut"
            :value="modelValue.rut ?? ''"
            type="text"
            placeholder="12.345.678-9"
            :class="['mt-1', fieldBase, fieldRing('rut')]"
            @input="update('rut', ($event.target as HTMLInputElement).value)"
          >
        </div>
      </div>

      <!-- Región -->
      <div>
        <label for="org-region" class="block text-sm font-medium text-navy-800">Región *</label>
        <select
          id="org-region"
          :value="modelValue.region"
          :aria-invalid="!!errors.region"
          :class="[
            'mt-1',
            fieldBase,
            fieldRing('region'),
            modelValue.region === '' ? 'text-slate-400' : ''
          ]"
          @change="update('region', ($event.target as HTMLSelectElement).value)"
          @blur="emit('field-touch', 'region')"
        >
          <option value="" disabled>Selecciona una región</option>
          <option
            v-for="region in regiones.filter((r) => r !== 'Todas las regiones')"
            :key="region"
            :value="region"
          >
            {{ region }}
          </option>
        </select>
        <p v-if="errors.region" class="mt-1 text-xs text-alert">
          {{ errors.region }}
        </p>
      </div>

      <!-- Dirección -->
      <div>
        <label for="org-direccion" class="block text-sm font-medium text-navy-800">Dirección *</label>
        <input
          id="org-direccion"
          :value="modelValue.direccion"
          type="text"
          autocomplete="street-address"
          placeholder="Calle, número, comuna"
          :aria-invalid="!!errors.direccion"
          :class="['mt-1', fieldBase, fieldRing('direccion')]"
          @input="update('direccion', ($event.target as HTMLInputElement).value)"
          @blur="emit('field-touch', 'direccion')"
        >
        <p v-if="errors.direccion" class="mt-1 text-xs text-alert">
          {{ errors.direccion }}
        </p>
      </div>
    </fieldset>

    <hr class="my-7 border-navy-800/10">

    <!-- ===== SECCIÓN 2 — Datos de contacto ===== -->
    <fieldset class="space-y-5">
      <legend class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
        Datos de contacto
      </legend>

      <!-- Nombre de contacto -->
      <div>
        <label for="org-contacto" class="block text-sm font-medium text-navy-800">
          Nombre de contacto *
        </label>
        <input
          id="org-contacto"
          :value="modelValue.contactoNombre"
          type="text"
          autocomplete="name"
          placeholder="Persona responsable de la organización"
          :aria-invalid="!!errors.contactoNombre"
          :class="['mt-1', fieldBase, fieldRing('contactoNombre')]"
          @input="update('contactoNombre', ($event.target as HTMLInputElement).value)"
          @blur="emit('field-touch', 'contactoNombre')"
        >
        <p v-if="errors.contactoNombre" class="mt-1 text-xs text-alert">
          {{ errors.contactoNombre }}
        </p>
      </div>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <!-- Email -->
        <div>
          <label for="org-email" class="block text-sm font-medium text-navy-800">
            Correo electrónico *
          </label>
          <input
            id="org-email"
            :value="modelValue.email"
            type="email"
            autocomplete="email"
            inputmode="email"
            placeholder="contacto@organizacion.cl"
            :aria-invalid="!!errors.email"
            :class="['mt-1', fieldBase, fieldRing('email')]"
            @input="update('email', ($event.target as HTMLInputElement).value)"
            @blur="emit('field-touch', 'email')"
          >
          <p v-if="errors.email" class="mt-1 text-xs text-alert">
            {{ errors.email }}
          </p>
        </div>

        <!-- Teléfono -->
        <div>
          <label for="org-telefono" class="block text-sm font-medium text-navy-800">
            Teléfono *
          </label>
          <input
            id="org-telefono"
            :value="modelValue.telefono"
            type="tel"
            autocomplete="tel"
            inputmode="tel"
            placeholder="+56 9 1234 5678"
            :aria-invalid="!!errors.telefono"
            :class="['mt-1', fieldBase, fieldRing('telefono')]"
            @input="update('telefono', ($event.target as HTMLInputElement).value)"
            @blur="emit('field-touch', 'telefono')"
          >
          <p v-if="errors.telefono" class="mt-1 text-xs text-alert">
            {{ errors.telefono }}
          </p>
        </div>
      </div>
    </fieldset>

    <hr class="my-7 border-navy-800/10">

    <!-- ===== SECCIÓN 3 — Credenciales ===== -->
    <fieldset class="space-y-5">
      <legend class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
        Credenciales
      </legend>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <!-- Contraseña -->
        <div>
          <label for="org-password" class="block text-sm font-medium text-navy-800">
            Contraseña *
          </label>
          <input
            id="org-password"
            :value="modelValue.password"
            type="password"
            autocomplete="new-password"
            placeholder="Mínimo 6 caracteres"
            :aria-invalid="!!errors.password"
            :class="['mt-1', fieldBase, fieldRing('password')]"
            @input="update('password', ($event.target as HTMLInputElement).value)"
            @blur="emit('field-touch', 'password')"
          >
          <p v-if="errors.password" class="mt-1 text-xs text-alert">
            {{ errors.password }}
          </p>
        </div>

        <!-- Confirmar contraseña -->
        <div>
          <label for="org-confirm-password" class="block text-sm font-medium text-navy-800">
            Confirmar contraseña *
          </label>
          <input
            id="org-confirm-password"
            :value="modelValue.confirmPassword"
            type="password"
            autocomplete="new-password"
            placeholder="Repite la contraseña"
            :aria-invalid="!!errors.confirmPassword"
            :class="['mt-1', fieldBase, fieldRing('confirmPassword')]"
            @input="update('confirmPassword', ($event.target as HTMLInputElement).value)"
            @blur="emit('field-touch', 'confirmPassword')"
          >
          <p v-if="errors.confirmPassword" class="mt-1 text-xs text-alert">
            {{ errors.confirmPassword }}
          </p>
        </div>
      </div>
    </fieldset>

    <hr class="my-7 border-navy-800/10">

    <!-- ===== SECCIÓN 4 — Documentación ===== -->
    <fieldset class="space-y-3">
      <legend class="font-display text-sm font-bold uppercase tracking-widest text-navy-600">
        Documentación
      </legend>
      <div>
        <label for="org-documento" class="block text-sm font-medium text-navy-800">
          Documento de respaldo (PDF o JPG) *
        </label>
        <input
          id="org-documento"
          type="file"
          accept=".pdf,.jpg,.jpeg"
          :aria-invalid="!!errors.document"
          class="mt-1 block w-full cursor-pointer rounded-lg bg-white text-sm text-navy-900
                 ring-1 ring-navy-600/20 file:mr-3 file:cursor-pointer file:rounded-md
                 file:border-0 file:bg-navy-600/10 file:px-3 file:py-2 file:text-sm
                 file:font-semibold file:text-navy-800 hover:file:bg-navy-600/20"
          @change="onDocumentInput"
          @blur="emit('field-touch', 'document')"
        >
        <p v-if="documentFile && !errors.document" class="mt-1 text-xs text-slate-500">
          {{ documentFile.name }}
        </p>
        <p v-if="errors.document" class="mt-1 text-xs text-alert">
          {{ errors.document }}
        </p>
        <p class="mt-2 text-sm text-navy-600">
          Certifica el respaldo legal o institucional de tu organización. Tu
          solicitud quedará pendiente de verificación por el equipo de Chile
          Aid antes de poder operar.
        </p>
      </div>
    </fieldset>

    <!-- Error global del envío -->
    <p
      v-if="submitError"
      role="alert"
      class="mt-7 rounded-lg bg-alert/10 px-4 py-3 text-sm font-semibold text-alert ring-1 ring-alert/40"
    >
      {{ submitError }}
    </p>

    <!-- Submit -->
    <div class="mt-7">
      <BaseButton
        type="submit"
        variant="navy"
        size="lg"
        :full-width="true"
        :disabled="!isFormValid || isLoading"
      >
        {{ isLoading ? 'Enviando solicitud…' : 'Solicitar verificación' }}
      </BaseButton>
      <p class="mt-3 text-center text-sm text-slate-500">
        Tu solicitud quedará pendiente de aprobación por el equipo de Chile Aid
        antes de poder operar en la plataforma.
      </p>
    </div>
  </form>
</template>
