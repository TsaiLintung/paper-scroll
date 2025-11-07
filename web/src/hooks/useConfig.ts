import { useCallback, useEffect, useState } from 'react'

import type { Config, Journal } from '../types'
import { useDataStore } from '../data/DataContext'

interface UseConfigResult {
  config: Config | null
  loading: boolean
  setField: <K extends keyof Config>(field: K, value: Config[K]) => Promise<void>
  addJournal: (journal: Journal) => Promise<void>
  removeJournal: (issn: string) => Promise<void>
  refresh: () => Promise<void>
}

export const useConfig = (): UseConfigResult => {
  const store = useDataStore()
  const [config, setConfig] = useState<Config | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    const next = await store.getConfig()
    setConfig(next)
    setLoading(false)
  }, [store])

  useEffect(() => {
    load()
  }, [load])

  const setField = useCallback(
    async <K extends keyof Config>(field: K, value: Config[K]) => {
      const next = await store.setConfigField(field, value)
      setConfig(next)
    },
    [store],
  )

  const addJournal = useCallback(
    async (journal: Journal) => {
      const next = await store.addJournal(journal)
      setConfig(next)
    },
    [store],
  )

  const removeJournal = useCallback(
    async (issn: string) => {
      const next = await store.removeJournal(issn)
      setConfig(next)
    },
    [store],
  )

  return {
    config,
    loading,
    setField,
    addJournal,
    removeJournal,
    refresh: load,
  }
}
