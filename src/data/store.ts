import type { Config, Journal } from '../types'
import { DEFAULT_CONFIG } from '../types'
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

  async addBlockPhrase(phrase: string): Promise<Config> {
    const config = await this.getConfig()
    const normalized = phrase.trim().toLowerCase()
    if (config.block_phrases.includes(normalized)) return config
    return writeConfig({ ...config, block_phrases: [...config.block_phrases, normalized] })
  }

  async removeBlockPhrase(phrase: string): Promise<Config> {
    const config = await this.getConfig()
    return writeConfig({ ...config, block_phrases: config.block_phrases.filter((p) => p !== phrase) })
  }

  async resetConfig(): Promise<Config> {
    const next: Config = {
      ...DEFAULT_CONFIG,
      journals: [...DEFAULT_CONFIG.journals],
    }
    return writeConfig(next)
  }
}
