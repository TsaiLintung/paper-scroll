import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import type { Config, Journal } from '../types'
import './SettingsPanel.css'
import closeIcon from '../assets/close-thin.svg'

interface SettingsPanelProps {
  config: Config
  onClose: () => void
  onUpdateField: <K extends keyof Config>(
    field: K,
    value: Config[K],
  ) => Promise<void> | void
  onAddJournal: (journal: Journal) => Promise<void> | void
  onRemoveJournal: (issn: string) => Promise<void> | void
  onReset: () => Promise<void> | void
}

export const SettingsPanel = ({
  config,
  onClose,
  onUpdateField,
  onAddJournal,
  onRemoveJournal,
  onReset,
}: SettingsPanelProps) => {
  const [journalName, setJournalName] = useState('')
  const [journalIssn, setJournalIssn] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [yearError, setYearError] = useState<string | null>(null)
  const [startYearInput, setStartYearInput] = useState(
    String(config.start_year),
  )
  const [endYearInput, setEndYearInput] = useState(String(config.end_year))

  useEffect(() => {
    setStartYearInput(String(config.start_year))
  }, [config.start_year])

  useEffect(() => {
    setEndYearInput(String(config.end_year))
  }, [config.end_year])

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

  const handleYearCommit = (
    field: 'start_year' | 'end_year',
    value: string,
  ) => {
    const trimmed = value.trim()
    if (!trimmed) {
      setYearError('Year is required.')
      return
    }
    const next = Number(trimmed)
    if (!Number.isInteger(next)) {
      setYearError('Year must be a whole number.')
      return
    }

    if (next < 1900 || next > 2100) {
      setYearError('Year must be between 1900 and 2100.')
      return
    }
    const otherValue =
      field === 'start_year' ? config.end_year : config.start_year
    if (field === 'start_year' && next > otherValue) {
      setYearError('Start year cannot be after end year.')
      return
    }
    if (field === 'end_year' && next < otherValue) {
      setYearError('End year cannot be before start year.')
      return
    }
    setYearError(null)
    onUpdateField(field, next)
    if (field === 'start_year') {
      setStartYearInput(String(next))
    } else {
      setEndYearInput(String(next))
    }
  }

  return (
    <aside className="settings-panel">
      <header className="settings-panel__header">
        <h2>Settings</h2>
        <button onClick={onClose} aria-label="Close settings">
          <img src={closeIcon} alt="" aria-hidden="true" />
        </button>
      </header>

      <section className="settings-panel__section">
        <h3>Year range</h3>
        <div className="settings-panel__grid settings-panel__grid--two">
          <label>
            Start
            <input
              type="number"
              min={1900}
              max={2100}
              value={startYearInput}
              onChange={(e) => {
                setStartYearInput(e.target.value)
                setYearError(null)
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  handleYearCommit('start_year', startYearInput)
                }
              }}
            />
          </label>
          <label>
            End
            <input
              type="number"
              min={1900}
              max={2100}
              value={endYearInput}
              onChange={(e) => {
                setEndYearInput(e.target.value)
                setYearError(null)
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  handleYearCommit('end_year', endYearInput)
                }
              }}
            />
          </label>
        </div>
        {yearError && <p className="settings-panel__error">{yearError}</p>}
      </section>

      <section className="settings-panel__section">
        <h3>Journals</h3>
        <form
          onSubmit={submitJournal}
          className="settings-panel__grid settings-panel__grid--form"
        >
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
              <button
                onClick={() => onRemoveJournal(journal.issn)}
                aria-label={`Remove ${journal.name}`}
              >
                <img src={closeIcon} alt="" aria-hidden="true" />
              </button>
            </span>
          ))}
        </div>
      </section>

      <section className="settings-panel__section">
        <h3>Other</h3>
        <div className="settings-panel__grid settings-panel__grid--two">
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
            Email
            <input
              type="email"
              value={config.email}
              onChange={(e) => onUpdateField('email', e.target.value)}
            />
          </label>
          <p className="settings-panel__note">
            Your email is stored locally and only used to sign OpenAlex API requests to increase the rate limit.
          </p>
        </div>
      </section>

      <div className="settings-panel__footer">
        <button
          type="button"
          className="settings-panel__reset-button"
          onClick={() => onReset()}
        >
          Reset preferences
        </button>
      </div>
    </aside>
  )
}
