import { defineConfig } from 'astro/config'
import cloudflare from '@astrojs/cloudflare'
import tailwind from '@astrojs/tailwind'
import react from '@astrojs/react'
import keystatic from '@keystatic/astro'

export default defineConfig({
  output: 'hybrid',
  adapter: cloudflare(),
  integrations: [
    tailwind(),
    react(),
    keystatic(),
  ],
  vite: {
    ssr: {
      external: [
        'node:path',
        'node:fs',
        'node:fs/promises',
        'node:os',
        'node:crypto',
        'node:process',
        'node:stream',
        'node:url',
      ],
    },
  },
})
