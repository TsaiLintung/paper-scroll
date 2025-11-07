import { useCallback, useEffect, useRef, useState } from 'react'

import { toPaperViewModel } from '../domain/paper'
import { sampleOpenAlexWork } from '../services/openalex'
import type { Config, PaperViewModel } from '../types'

const INITIAL_BATCH = 5
const LOAD_MORE_BATCH = 3

const pickRandomItem = <T,>(items: T[]): T =>
  items[Math.floor(Math.random() * items.length)]

interface UsePaperFeedOptions {
  onPaperError?: (message: string) => void
}

const pickYear = (start: number, end: number) => {
  const span = end - start + 1
  return start + Math.floor(Math.random() * Math.max(span, 1))
}

export const usePaperFeed = (
  config: Config | null,
  options: UsePaperFeedOptions = {},
) => {
  const { onPaperError } = options
  const [papers, setPapers] = useState<PaperViewModel[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const isFetchingRef = useRef(false)
  const seenIdsRef = useRef<Set<string>>(new Set())
  const paperErrorRef = useRef(onPaperError)

  useEffect(() => {
    paperErrorRef.current = onPaperError
  }, [onPaperError])

  const pickTarget = useCallback(() => {
    if (!config) {
      return null
    }
    const journals = config.journals
    if (!journals.length) {
      setError('Add at least one journal to start sampling papers.')
      return null
    }
    const journal = pickRandomItem(journals)
    const year = pickYear(config.start_year, config.end_year)
    return { journal, year }
  }, [config])

  const samplePaper = useCallback(async () => {
    const target = pickTarget()
    if (!target) {
      return { paper: null, canRetry: false }
    }
    const { journal, year } = target
    try {
      const work = await sampleOpenAlexWork({
        issn: journal.issn,
        year,
        email: config?.email,
      })
      setError(null)
      return { paper: toPaperViewModel(work), canRetry: true }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to fetch paper data.'
      setError(message)
      paperErrorRef.current?.(message)
      return { paper: null, canRetry: true }
    }
  }, [config?.email, pickTarget])

  const loadBatch = useCallback(
    async (count: number) => {
      const batch: PaperViewModel[] = []
      let attempts = 0
      const maxAttempts = count * 5
      while (batch.length < count && attempts < maxAttempts) {
        attempts += 1
        const { paper, canRetry } = await samplePaper()
        if (paper) {
          if (seenIdsRef.current.has(paper.id)) {
            continue
          }
          seenIdsRef.current.add(paper.id)
          batch.push(paper)
        } else if (!canRetry) {
          break
        }
      }
      return batch
    },
    [samplePaper],
  )

  const loadInitial = useCallback(async () => {
    if (!config) {
      return
    }
    setIsLoading(true)
    seenIdsRef.current.clear()
    const batch = await loadBatch(INITIAL_BATCH)
    setPapers(batch)
    setIsLoading(false)
  }, [config, loadBatch])

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
    loadMore,
  }
}
