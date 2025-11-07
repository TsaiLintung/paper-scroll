import { useCallback, useEffect, useMemo, useState } from 'react'

import { toPaperViewModel } from '../domain/paper'
import type { OpenAlexWork, PaperViewModel } from '../types'

const seedWork: OpenAlexWork = {
  id: 'https://openalex.org/W123456789',
  doi: '10.1038/s41586-020-2649-2',
  display_name: 'Learning from Web-only Research Feeds',
  publication_year: 2021,
  abstract_inverted_index: {
    Learning: [0],
    from: [1],
    modern: [2],
    research: [3],
    feeds: [4],
  },
  primary_location: {
    source: {
      display_name: 'Journal of Browser Science',
    },
  },
  authorships: [
    {
      author: {
        display_name: 'Ada Lovelace',
      },
    },
    {
      author: {
        display_name: 'Grace Hopper',
      },
    },
  ],
}

const extendSeedPaper = (index: number): OpenAlexWork => ({
  ...seedWork,
  id: `${seedWork.id}-${index}`,
  publication_year: seedWork.publication_year ?? 2021 + index,
})

export const usePaperFeed = () => {
  const [papers, setPapers] = useState<PaperViewModel[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const buildSeed = useMemo(() => {
    const views = Array.from({ length: 5 }).map((_, idx) =>
      toPaperViewModel(extendSeedPaper(idx)),
    )
    return views
  }, [])

  useEffect(() => {
    setPapers(buildSeed)
    setIsLoading(false)
  }, [buildSeed])

  const refresh = useCallback(() => {
    setIsLoading(true)
    setTimeout(() => {
      setPapers(buildSeed)
      setIsLoading(false)
    }, 250)
  }, [buildSeed])

  const loadMore = useCallback(() => {
    setPapers((prev) => [
      ...prev,
      ...Array.from({ length: 3 }).map((_, idx) =>
        toPaperViewModel(extendSeedPaper(prev.length + idx)),
      ),
    ])
  }, [])

  return {
    papers,
    isLoading,
    refresh,
    loadMore,
  }
}
