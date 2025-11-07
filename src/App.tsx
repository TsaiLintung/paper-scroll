import './App.css'
import { ExploreView } from './components/ExploreView'
import { SettingsPanel } from './components/SettingsPanel'
import { Toast, type ToastKind } from './components/Toast'
import { useConfig } from './hooks/useConfig'
import { usePaperFeed } from './hooks/usePaperFeed'
import { useCallback, useEffect, useState } from 'react'
import type { Config, Journal } from './types'

function App() {
  const { config, loading, setField, addJournal, removeJournal } = useConfig()
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [toast, setToast] = useState<null | { message: string; kind: ToastKind }>(
    null,
  )

  const showToast = useCallback(
    (message: string, kind: ToastKind = 'info') => {
      setToast({ message, kind })
    },
    [],
  )

  const { papers, isLoading, error, refresh, loadMore } = usePaperFeed(config, {
    onPaperError: (message) => showToast(message, 'error'),
  })

  useEffect(() => {
    if (config?.text_size) {
      document.documentElement.style.setProperty(
        '--base-text-size',
        `${config.text_size}px`,
      )
    }
  }, [config?.text_size])

  const handleFieldUpdate = useCallback(
    async <K extends keyof Config>(field: K, value: Config[K]) => {
      await setField(field, value)
    },
    [setField],
  )

  const handleAddJournal = useCallback(
    async (journal: Journal) => {
      await addJournal(journal)
    },
    [addJournal],
  )

  const handleRemoveJournal = useCallback(
    async (issn: string) => {
      await removeJournal(issn)
    },
    [removeJournal],
  )

  if (loading || !config) {
    return (
      <div className="app-loading">
        <p>Loading configuration…</p>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <ExploreView
        papers={papers}
        isLoading={isLoading}
        error={error}
        onRefresh={refresh}
        onLoadMore={loadMore}
        onToggleSettings={() => setSettingsOpen((prev) => !prev)}
      />
      <div
        className={`settings-overlay ${settingsOpen ? 'is-visible' : ''}`}
        onClick={() => setSettingsOpen(false)}
      >
        <div
          className="settings-overlay__panel"
          onClick={(e) => e.stopPropagation()}
        >
          <SettingsPanel
            config={config}
            onClose={() => setSettingsOpen(false)}
            onUpdateField={handleFieldUpdate}
            onAddJournal={handleAddJournal}
            onRemoveJournal={handleRemoveJournal}
          />
        </div>
      </div>
      {toast && (
        <Toast
          message={toast.message}
          kind={toast.kind}
          onClose={() => setToast(null)}
        />
      )}
      <footer className="app-footer">
        Powered by OpenAlex · © Lin-Tung Tsai
      </footer>
    </div>
  )
}

export default App
