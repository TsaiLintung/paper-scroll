import './App.css'
import { ExploreView } from './components/ExploreView'
import { SettingsPanel } from './components/SettingsPanel'
import { Toast, type ToastKind } from './components/Toast'
import { useConfig } from './hooks/useConfig'
import { usePaperFeed } from './hooks/usePaperFeed'
import { useStatus } from './hooks/useStatus'
import { useSyncService } from './hooks/useSyncService'
import { useCallback, useEffect, useRef, useState } from 'react'
import type { Config, Journal } from './types'
import { useDataStore } from './data/DataContext'

const SYNC_SENSITIVE_FIELDS: Array<keyof Config> = [
  'start_year',
  'end_year',
  'email',
]

function App() {
  const { config, loading, setField, addJournal, removeJournal } = useConfig()
  const { status } = useStatus()
  const { papers, isLoading, error, refresh, loadMore } = usePaperFeed(config)
  const { start: startSync, isRunning: isSyncing } = useSyncService()
  const store = useDataStore()
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [toast, setToast] = useState<null | { message: string; kind: ToastKind }>(
    null,
  )
  const coldStartSyncTriggered = useRef(false)

  const showToast = useCallback(
    (message: string, kind: ToastKind = 'info') => {
      setToast({ message, kind })
    },
    [],
  )

  useEffect(() => {
    if (config?.text_size) {
      document.documentElement.style.setProperty(
        '--base-text-size',
        `${config.text_size}px`,
      )
    }
  }, [config?.text_size])

  const runSync = useCallback(
    async ({
      configOverride,
      silent = false,
    }: { configOverride?: Config; silent?: boolean } = {}) => {
      const target = configOverride ?? config
      if (!target || isSyncing) {
        return
      }
      try {
        await startSync(target)
        if (!silent) {
          showToast('Journals updated.')
        }
      } catch (err) {
        showToast(
          err instanceof Error ? err.message : 'Failed to update journals.',
          'error',
        )
      }
    },
    [config, isSyncing, showToast, startSync],
  )

  const handleFieldUpdate = useCallback(
    async <K extends keyof Config>(field: K, value: Config[K]) => {
      const next = await setField(field, value)
      if (SYNC_SENSITIVE_FIELDS.includes(field)) {
        await runSync({ configOverride: next, silent: true })
      }
    },
    [runSync, setField],
  )

  const handleAddJournal = useCallback(
    async (journal: Journal) => {
      const next = await addJournal(journal)
      await runSync({ configOverride: next, silent: true })
    },
    [addJournal, runSync],
  )

  const handleRemoveJournal = useCallback(
    async (issn: string) => {
      const next = await removeJournal(issn)
      await runSync({ configOverride: next, silent: true })
    },
    [removeJournal, runSync],
  )

  const handleManualSync = useCallback(() => {
    void runSync()
  }, [runSync])

  useEffect(() => {
    if (!config || coldStartSyncTriggered.current) {
      return
    }
    coldStartSyncTriggered.current = true

    let active = true
    void (async () => {
      try {
        const snapshots = await store.getSnapshots()
        if (!active || snapshots.length > 0) {
          return
        }
        await runSync({ silent: true })
      } catch (err) {
        console.error('Failed to evaluate cold-start sync', err)
      }
    })()

    return () => {
      active = false
    }
  }, [config, runSync, store])

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
            status={status}
            onClose={() => setSettingsOpen(false)}
            onUpdateField={handleFieldUpdate}
            onAddJournal={handleAddJournal}
            onRemoveJournal={handleRemoveJournal}
            onSync={handleManualSync}
            isSyncing={isSyncing}
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
    </div>
  )
}

export default App
