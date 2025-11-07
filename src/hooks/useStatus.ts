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
    refresh()
    const interval = setInterval(() => {
      store.getStatus().then((payload) => {
        if (payload && mounted) {
          setStatus(payload)
        }
      })
    }, 1000)
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [refresh, store])

  const update = useCallback(
    async (payload: StatusPayload) => {
      await store.saveStatus(payload)
      setStatus(payload)
    },
    [store],
  )

  return { status, refresh, update }
}
