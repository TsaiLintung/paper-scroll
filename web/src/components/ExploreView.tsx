import { useCallback, useRef } from 'react'

import type { PaperViewModel } from '../types'
import { PaperCard } from './PaperCard'
import './ExploreView.css'

interface ExploreViewProps {
  papers: PaperViewModel[]
  isLoading: boolean
  error?: string | null
  onRefresh: () => void
  onLoadMore: () => void
  onToggleSettings: () => void
}

export const ExploreView = ({
  papers,
  isLoading,
  error,
  onRefresh,
  onLoadMore,
  onToggleSettings,
}: ExploreViewProps) => {
  const listRef = useRef<HTMLDivElement | null>(null)

  const handleScroll = useCallback(() => {
    const target = listRef.current
    if (!target || isLoading) {
      return
    }
    const { scrollTop, scrollHeight, clientHeight } = target
    if (scrollTop + clientHeight >= scrollHeight - 200) {
      onLoadMore()
    }
  }, [isLoading, onLoadMore])

  return (
    <section className="explore-view">
      <header className="explore-view__header">
        <h1>PAPERSCROLL</h1>
        <div className="explore-view__actions">
          <button onClick={onRefresh}>Refresh</button>
          <button onClick={onToggleSettings}>Settings</button>
        </div>
      </header>
      <div className="explore-view__list" ref={listRef} onScroll={handleScroll}>
        {error && <div className="explore-view__error">{error}</div>}
        {papers.map((paper, idx) => (
          <div key={paper.id}>
            {idx > 0 && <div className="explore-view__divider" />}
            <PaperCard paper={paper} />
          </div>
        ))}
        {isLoading && (
          <div className="explore-view__loading">Loading more papers…</div>
        )}
      </div>
    </section>
  )
}
