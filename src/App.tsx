import './App.css'
import { ExploreView } from './components/ExploreView'
import { SettingsPanel } from './components/SettingsPanel'
import { Toast, type ToastKind } from './components/Toast'
import { useConfig } from './hooks/useConfig'
import { usePaperFeed } from './hooks/usePaperFeed'
import { useCallback, useEffect, useState } from 'react'
import type { Config, Journal } from './types'

function App() {
  const { config, loading, setField, addJournal, removeJournal, resetConfig } =
    useConfig()
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [toast, setToast] = useState<null | { message: string; kind: ToastKind }>(
    null,
  )
  const [emailPromptShown, setEmailPromptShown] = useState(false)

  const showToast = useCallback(
    (message: string, kind: ToastKind = 'info') => {
      setToast({ message, kind })
    },
    [],
  )

  const { papers, isLoading, error, loadMore } = usePaperFeed(config, {
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

  useEffect(() => {
    if (config && !config.email?.trim() && !emailPromptShown) {
      showToast('Enter email in settings to increase load speed.', 'info')
      setEmailPromptShown(true)
    }
  }, [config, emailPromptShown, showToast])

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

  const handleResetPreferences = useCallback(async () => {
    await resetConfig()
    showToast('Preferences reset to defaults.', 'info')
  }, [resetConfig, showToast])

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
          <div className="settings-overlay__body">
            <SettingsPanel
              config={config}
              onClose={() => setSettingsOpen(false)}
              onUpdateField={handleFieldUpdate}
              onAddJournal={handleAddJournal}
              onRemoveJournal={handleRemoveJournal}
              onReset={handleResetPreferences}
            />
          </div>
          <footer className="settings-overlay__footer">
            Powered by{' '}
            <a href="https://openalex.org/" target="_blank" rel="noreferrer">
              OpenAlex
            </a>{' '}
            · ©{' '}
            <a
              href="https://github.com/TsaiLintung/paper-scroll"
              target="_blank"
              rel="noreferrer"
            >
              Lin-Tung Tsai
            </a>
          </footer>
        </div>
      </div>
      {toast && (
        <Toast
          message={toast.message}
          kind={toast.kind}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  )
}

export default App
