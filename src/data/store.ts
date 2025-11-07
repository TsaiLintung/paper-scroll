import type { Config, Journal } from '../types'
import { readConfig, updateConfig, writeConfig } from './db'

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
}
