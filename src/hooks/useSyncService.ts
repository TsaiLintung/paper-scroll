import { useEffect, useMemo, useState } from 'react'

import { useDataStore } from '../data/DataContext'
import { SyncService } from '../services/sync'
import type { Config } from '../types'

export const useSyncService = () => {
  const store = useDataStore()
  const service = useMemo(() => new SyncService(store), [store])
  const [isRunning, setIsRunning] = useState(false)

  useEffect(
    () => () => {
      service.dispose()
    },
    [service],
  )

  const start = async (config: Config) => {
    setIsRunning(true)
    try {
      await service.start(config)
    } finally {
      setIsRunning(false)
    }
  }

  return { start, isRunning }
}
