import { useCallback, useRef } from 'react'

import type { PaperViewModel } from '../types'
import { PaperCard } from './PaperCard'
import './ExploreView.css'
import settingsIcon from '../assets/settings-thin.svg'

interface ExploreViewProps {
  papers: PaperViewModel[]
  isLoading: boolean
  error?: string | null
  onLoadMore: () => void
  onToggleSettings: () => void
}

export const ExploreView = ({
  papers,
  isLoading,
  error,
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
          <button
            type="button"
            onClick={onToggleSettings}
            aria-label="Open settings"
          >
            <img src={settingsIcon} alt="" aria-hidden="true" />
          </button>
        </div>
      </header>
      <div className="explore-view__list" ref={listRef} onScroll={handleScroll}>
        <div className="explore-view__list-inner">
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
      </div>
    </section>
  )
}
