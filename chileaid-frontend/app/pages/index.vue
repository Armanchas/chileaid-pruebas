<script setup lang="ts">
/**
 * PÁGINA — Solo orquesta. Toma el ViewModel y reparte su estado/acciones a
 * los componentes vía props/eventos. No contiene lógica de negocio ni datos.
 */
import { useLandingViewModel } from '~/composables/useLandingViewModel'
import HeaderSection from '~/components/landing/HeaderSection.vue'
import HeroSection from '~/components/landing/HeroSection.vue'
import StatsSection from '~/components/landing/StatsSection.vue'
import TutorialSection from '~/components/landing/TutorialSection.vue'
import FooterSection from '~/components/landing/FooterSection.vue'

const {
  hero,
  heroImages,
  stats,
  tutorial,
  emergencyNumbers,
  loadLanding,
  onDonate,
  onRegisterCenter,
  onViewMap
} = useLandingViewModel()

// Carga los datos en el servidor durante el render (SSR-friendly).
await loadLanding()
</script>

<template>
  <div>
    <HeaderSection
      @donate="onDonate"
      @emergency="onDonate"
      @account="navigateTo('/login')"
    />

    <main>
      <HeroSection
        :content="hero"
        :images="heroImages"
        :stats="stats"
        @donate="onDonate"
        @register-center="onRegisterCenter"
        @view-map="onViewMap"
      />

      <StatsSection :stats="stats" />

      <TutorialSection
        :tracks="tutorial"
        @select="(id) => (id === 'organizacion' ? onRegisterCenter() : onDonate())"
      />
    </main>

    <FooterSection :emergency-numbers="emergencyNumbers" />
  </div>
</template>
