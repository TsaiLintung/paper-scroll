import { useState } from 'react'
import type { FormEvent } from 'react'

import type { Config, Journal, StatusPayload } from '../types'
import './SettingsPanel.css'

interface SettingsPanelProps {
  config: Config
  status: StatusPayload | null
  onClose: () => void
  onUpdateField: <K extends keyof Config>(
    field: K,
    value: Config[K],
  ) => Promise<void> | void
  onAddJournal: (journal: Journal) => Promise<void> | void
  onRemoveJournal: (issn: string) => Promise<void> | void
  onSync: () => Promise<void> | void
}

export const SettingsPanel = ({
  config,
  status,
  onClose,
  onUpdateField,
  onAddJournal,
  onRemoveJournal,
  onSync,
}: SettingsPanelProps) => {
  const [journalName, setJournalName] = useState('')
  const [journalIssn, setJournalIssn] = useState('')
  const [error, setError] = useState<string | null>(null)

  const submitJournal = (event: FormEvent) => {
    event.preventDefault()
    if (!journalName.trim() || !journalIssn.trim()) {
      setError('Name and ISSN are required.')
      return
    }
    onAddJournal({ name: journalName.trim(), issn: journalIssn.trim() })
    setJournalName('')
    setJournalIssn('')
    setError(null)
  }

  return (
    <aside className="settings-panel">
      <header className="settings-panel__header">
        <h2>Settings</h2>
        <button onClick={onClose}>Close</button>
      </header>

      <section className="settings-panel__section">
        <h3>Year range</h3>
        <div className="settings-panel__grid">
          <label>
            Start
            <input
              type="number"
              value={config.start_year}
              onChange={(e) => onUpdateField('start_year', Number(e.target.value))}
            />
          </label>
          <label>
            End
            <input
              type="number"
              value={config.end_year}
              onChange={(e) => onUpdateField('end_year', Number(e.target.value))}
            />
          </label>
        </div>
      </section>

      <section className="settings-panel__section">
        <h3>Journals</h3>
        <form onSubmit={submitJournal} className="settings-panel__grid">
          <label>
            Name
            <input
              value={journalName}
              maxLength={32}
              onChange={(e) => setJournalName(e.target.value)}
            />
          </label>
          <label>
            ISSN
            <input
              value={journalIssn}
              maxLength={12}
              onChange={(e) => setJournalIssn(e.target.value)}
            />
          </label>
          <button type="submit">Add</button>
        </form>
        {error && <p className="settings-panel__error">{error}</p>}
        <div className="settings-panel__chip-row">
          {config.journals.map((journal) => (
            <span key={journal.issn} className="settings-panel__chip">
              {journal.name} · {journal.issn}
              <button onClick={() => onRemoveJournal(journal.issn)}>×</button>
            </span>
          ))}
        </div>
      </section>

      <section className="settings-panel__section">
        <h3>Appearance</h3>
        <label>
          Text size
          <input
            type="number"
            min={12}
            max={30}
            value={config.text_size}
            onChange={(e) => onUpdateField('text_size', Number(e.target.value))}
          />
        </label>
        <label>
          Contact email
          <input
            type="email"
            value={config.email}
            onChange={(e) => onUpdateField('email', e.target.value)}
          />
        </label>
      </section>

      <section className="settings-panel__section">
        <h3>Journal sync</h3>
        <button onClick={onSync}>Update journals</button>
        <p className="settings-panel__status-text">
          {status?.message ?? 'Idle'}
        </p>
        <progress value={status?.progress ?? 0} max={1} />
      </section>
    </aside>
  )
}
