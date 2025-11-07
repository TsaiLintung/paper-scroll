import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

const repoBase = '/paper-scroll/'

export default defineConfig({
  base: repoBase,
  plugins: [react()],
  test: {
    globals: true,
    environment: 'node',
  },
})
