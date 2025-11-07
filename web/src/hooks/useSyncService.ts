import { useMemo } from 'react'

import { useDataStore } from '../data/DataContext'
import { SyncService } from '../services/sync'

export const useSyncService = () => {
  const store = useDataStore()
  return useMemo(() => new SyncService(store), [store])
}
