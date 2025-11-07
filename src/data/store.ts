import type { Config, Journal, JournalSnapshot, PaperRecord, StatusPayload } from '../types'
import {
  cachePaper,
  getCachedPaper,
  listJournalSnapshots,
  readConfig,
  readStatus,
  saveJournalSnapshot,
  updateConfig,
  writeConfig,
  writeStatus,
} from './db'

export class DataStore {
  async getConfig(): Promise<Config> {
    return readConfig()
  }

  async setConfigField<K extends keyof Config>(field: K, value: Config[K]): Promise<Config> {
    return updateConfig({ [field]: value } as Partial<Config>)
  }

  async addJournal(journal: Journal): Promise<Config> {
    const config = await this.getConfig()
    const exists = config.journals.some(
      (entry) => entry.issn === journal.issn || entry.name === journal.name,
    )
    if (exists) {
      return config
    }
    const next: Config = {
      ...config,
      journals: [...config.journals, journal],
    }
    return writeConfig(next)
  }

  async removeJournal(issn: string): Promise<Config> {
    const config = await this.getConfig()
    const next: Config = {
      ...config,
      journals: config.journals.filter((journal) => journal.issn !== issn),
    }
    return writeConfig(next)
  }

  async saveSnapshot(snapshot: JournalSnapshot): Promise<void> {
    await saveJournalSnapshot(snapshot)
  }

  async getSnapshots(): Promise<JournalSnapshot[]> {
    return listJournalSnapshots()
  }

  async saveStatus(status: StatusPayload): Promise<void> {
    await writeStatus(status)
  }

  async getStatus(): Promise<StatusPayload | undefined> {
    return readStatus()
  }

  async rememberPaper(record: PaperRecord): Promise<void> {
    await cachePaper(record)
  }

  async getPaper(doi: string): Promise<PaperRecord | undefined> {
    return getCachedPaper(doi)
  }
}
