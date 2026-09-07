import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  theme: {
    extend: {
      colors: {
        // Azules profundos 
        navy: {
          DEFAULT: '#002675',
          900: '#001640',
          800: '#002675',
          600: '#0039a6',
          500: '#0046cc',
        },
        // Rojo alerta 
        alert: {
          DEFAULT: '#8d0001',
          600: '#b00002',
          500: '#d11a1c',
        },
        surface: '#f8f9fa',
      },
      fontFamily: {
        display: ['"Barlow Condensed"', 'Oswald', 'sans-serif'],
        body: ['"Barlow Condensed"', 'system-ui', 'sans-serif'],
      },
    },
  },
}
