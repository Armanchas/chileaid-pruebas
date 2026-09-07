<script setup lang="ts">
/**
 * VIEW (UI) — Botón base reutilizable. Solo recibe props y emite `click`.
 * No conoce servicios ni composables.
 */
interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'navy'
  size?: 'md' | 'lg'
  type?: 'button' | 'submit'
  fullWidth?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  fullWidth: false,
  disabled: false
})

defineEmits<{ click: [] }>()

const variantClasses: Record<NonNullable<Props['variant']>, string> = {
  primary:
    'bg-alert text-white hover:bg-alert-600 shadow-lg shadow-alert/30 hover:shadow-alert/40',
  navy:
    'bg-navy-800 text-white hover:bg-navy-600 shadow-lg shadow-navy-800/25 hover:shadow-navy-800/40',
  secondary:
    'glass text-white hover:bg-white/20 border-white/30',
  ghost:
    'bg-transparent text-navy-600 hover:bg-navy-600/10'
}

const sizeClasses: Record<NonNullable<Props['size']>, string> = {
  md: 'px-6 py-3 text-base',
  lg: 'px-8 py-4 text-lg'
}
</script>

<template>
  <button
    :type="props.type"
    :disabled="props.disabled"
    :class="[
      'inline-flex items-center justify-center gap-2 rounded-lg font-display font-bold uppercase tracking-wide',
      'transition-all duration-200 ease-out hover:-translate-y-0.5 active:translate-y-0',
      'focus:outline-none focus-visible:ring-4 focus-visible:ring-white/40',
      'disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none disabled:hover:translate-y-0',
      variantClasses[props.variant],
      sizeClasses[props.size],
      props.fullWidth ? 'w-full' : ''
    ]"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>
