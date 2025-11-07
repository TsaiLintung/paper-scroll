import { useCallback, useEffect, useState } from 'react'

import type { Config, Journal } from '../types'
import { useDataStore } from '../data/DataContext'

interface UseConfigResult {
  config: Config | null
  loading: boolean
  setField: <K extends keyof Config>(field: K, value: Config[K]) => Promise<Config>
  addJournal: (journal: Journal) => Promise<Config>
  removeJournal: (issn: string) => Promise<Config>
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

  const apply = useCallback(
    async (mutate: () => Promise<Config>) => {
      const next = await mutate()
      setConfig(next)
      return next
    },
    [setConfig],
  )

  const setField = useCallback(
    async <K extends keyof Config>(field: K, value: Config[K]) => {
      return apply(() => store.setConfigField(field, value))
    },
    [apply, store],
  )

  const addJournal = useCallback(
    async (journal: Journal) => {
      return apply(() => store.addJournal(journal))
    },
    [apply, store],
  )

  const removeJournal = useCallback(
    async (issn: string) => {
      return apply(() => store.removeJournal(issn))
    },
    [apply, store],
  )

  return {
    config,
    loading,
    setField,
    addJournal,
    removeJournal,
  }
}
