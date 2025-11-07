import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

const RELATIVE_BASE = './'
const DEV_BASE = '/'

export default defineConfig(({ mode }) => {
  const base =
    process.env.VITE_PUBLIC_BASE ??
    (mode === 'production' ? RELATIVE_BASE : DEV_BASE)

  return {
    base,
    plugins: [react()],
    test: {
      globals: true,
      environment: 'node',
    },
  }
})
