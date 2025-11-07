import { useCallback, useEffect, useRef, useState } from 'react'

import { useDataStore } from '../data/DataContext'
import { toPaperViewModel } from '../domain/paper'
import { fetchOpenAlexWork } from '../services/openalex'
import type { Config, PaperViewModel } from '../types'

const DEFAULT_DOI = '10.1038/s41586-020-2649-2'
const INITIAL_BATCH = 5
const LOAD_MORE_BATCH = 3

const shuffle = <T,>(input: T[]): T[] => {
  const copy = [...input]
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy
}

export const usePaperFeed = (config: Config | null) => {
  const store = useDataStore()
  const [papers, setPapers] = useState<PaperViewModel[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const doiPoolRef = useRef<string[]>([])
  const isFetchingRef = useRef(false)

  const loadSnapshotsIntoPool = useCallback(async () => {
    const snapshots = await store.getSnapshots()
    const pool = snapshots.flatMap((snapshot) =>
      snapshot.items.map((item) => item.DOI).filter(Boolean),
    )
    if (pool.length === 0) {
      doiPoolRef.current = [DEFAULT_DOI]
      setError('No journal data yet. Run “Update journals” to fetch metadata.')
      return false
    }
    doiPoolRef.current = shuffle(pool)
    setError(null)
    return true
  }, [store])

  const dequeueDoi = async () => {
    if (doiPoolRef.current.length === 0) {
      await loadSnapshotsIntoPool()
    }
    return doiPoolRef.current.shift() ?? DEFAULT_DOI
  }

  const fetchWork = useCallback(
    async (doi: string) => {
      const cached = await store.getPaper(doi)
      if (cached) {
        return cached.payload
      }
      const work = await fetchOpenAlexWork(doi, config?.email)
      await store.rememberPaper({
        doi,
        payload: work,
        cached_at: Date.now(),
      })
      return work
    },
    [config?.email, store],
  )

  const loadBatch = useCallback(
    async (count: number) => {
      const batch: PaperViewModel[] = []
      for (let i = 0; i < count; i += 1) {
        const doi = await dequeueDoi()
        try {
          const work = await fetchWork(doi)
          batch.push(toPaperViewModel(work))
        } catch (err) {
          setError(
            err instanceof Error ? err.message : 'Failed to fetch paper data.',
          )
        }
      }
      return batch
    },
    [fetchWork],
  )

  const loadInitial = useCallback(async () => {
    if (!config) {
      return
    }
    setIsLoading(true)
    setError(null)
    await loadSnapshotsIntoPool()
    const batch = await loadBatch(INITIAL_BATCH)
    setPapers(batch)
    setIsLoading(false)
  }, [config, loadBatch, loadSnapshotsIntoPool])

  const loadMore = useCallback(async () => {
    if (isFetchingRef.current || !config) {
      return
    }
    isFetchingRef.current = true
    const batch = await loadBatch(LOAD_MORE_BATCH)
    setPapers((prev) => [...prev, ...batch])
    isFetchingRef.current = false
  }, [config, loadBatch])

  useEffect(() => {
    loadInitial()
  }, [loadInitial])

  const refresh = useCallback(() => {
    loadInitial()
  }, [loadInitial])

  return {
    papers,
    isLoading,
    error,
    refresh,
    loadMore,
  }
}
