import './App.css'
import { ExploreView } from './components/ExploreView'
import { SettingsPanel } from './components/SettingsPanel'
import { useConfig } from './hooks/useConfig'
import { usePaperFeed } from './hooks/usePaperFeed'
import { useStatus } from './hooks/useStatus'
import { useSyncService } from './hooks/useSyncService'
import { useEffect, useState } from 'react'

function App() {
  const { config, loading, setField, addJournal, removeJournal } = useConfig()
  const { status } = useStatus()
  const { papers, isLoading, refresh, loadMore } = usePaperFeed()
  const syncService = useSyncService()
  const [settingsOpen, setSettingsOpen] = useState(false)

  useEffect(() => {
    if (config?.text_size) {
      document.documentElement.style.setProperty(
        '--base-text-size',
        `${config.text_size}px`,
      )
    }
  }, [config?.text_size])

  const handleSync = async () => {
    await syncService.startSync()
  }

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
            status={status}
            onClose={() => setSettingsOpen(false)}
            onUpdateField={setField}
            onAddJournal={addJournal}
            onRemoveJournal={removeJournal}
            onSync={handleSync}
          />
        </div>
      </div>
    </div>
  )
}

export default App
