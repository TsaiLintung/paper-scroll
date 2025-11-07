import { useCallback, useEffect, useState } from 'react'

import type { StatusPayload } from '../types'
import { useDataStore } from '../data/DataContext'

export const useStatus = () => {
  const store = useDataStore()
  const [status, setStatus] = useState<StatusPayload | null>(null)

  const refresh = useCallback(async () => {
    const payload = await store.getStatus()
    if (payload) {
      setStatus(payload)
    }
  }, [store])

  useEffect(() => {
    let mounted = true
    const tick = () => {
      refresh().catch(() => {
        /* ignore polling errors */
      })
    }
    tick()
    const interval = setInterval(() => {
      if (mounted) {
        tick()
      }
    }, 1000)
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [refresh])

  return { status }
}
