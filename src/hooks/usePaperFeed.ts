import { useCallback, useEffect, useRef, useState } from 'react'

import { useDataStore } from '../data/DataContext'
import { toPaperViewModel } from '../domain/paper'
import { fetchOpenAlexWork } from '../services/openalex'
import type { Config, PaperViewModel } from '../types'

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
      setError('No journal data yet. Run “Update journals” to fetch metadata.')
      return false
    }
    doiPoolRef.current = shuffle(pool)
    setError(null)
    return true
  }, [store])

  const ensurePoolHasEntries = useCallback(async () => {
    if (doiPoolRef.current.length > 0) {
      return true
    }
    return loadSnapshotsIntoPool()
  }, [loadSnapshotsIntoPool])

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
      })
      return work
    },
    [config?.email, store],
  )

  const loadBatch = useCallback(
    async (count: number) => {
      const hasPool = await ensurePoolHasEntries()
      if (!hasPool) {
        return []
      }
      const batch: PaperViewModel[] = []
      let attempts = 0
      const maxAttempts = count * 5
      while (batch.length < count && attempts < maxAttempts) {
        attempts += 1
        const doi = doiPoolRef.current.shift()
        if (!doi) {
          break
        }
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
    [ensurePoolHasEntries, fetchWork],
  )

  const loadInitial = useCallback(async () => {
    if (!config) {
      return
    }
    setIsLoading(true)
    const populatedPool = await loadSnapshotsIntoPool()
    if (populatedPool) {
      const batch = await loadBatch(INITIAL_BATCH)
      setPapers(batch)
    } else {
      setPapers([])
    }
    setIsLoading(false)
  }, [config, loadBatch, loadSnapshotsIntoPool])

  const loadMore = useCallback(async () => {
    if (isFetchingRef.current || !config) {
      return
    }
    isFetchingRef.current = true
    const batch = await loadBatch(LOAD_MORE_BATCH)
    if (batch.length) {
      setPapers((prev) => [...prev, ...batch])
    }
    isFetchingRef.current = false
  }, [config, loadBatch])

  useEffect(() => {
    loadInitial()
  }, [loadInitial])

  return {
    papers,
    isLoading,
    error,
    refresh: loadInitial,
    loadMore,
  }
}
