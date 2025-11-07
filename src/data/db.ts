import type { Config } from '../types'
import { DEFAULT_CONFIG } from '../types'

const STORAGE_KEY = 'paper-scroll:config'

const getStorage = (): Storage | null => {
  if (typeof window === 'undefined' || !window.localStorage) {
    return null
  }
  return window.localStorage
}

const readFromStorage = (): Config | null => {
  const storage = getStorage()
  if (!storage) {
    return null
  }
  const raw = storage.getItem(STORAGE_KEY)
  if (!raw) {
    return null
  }
  try {
    return JSON.parse(raw) as Config
  } catch (err) {
    console.warn('Failed to parse stored config, resetting.', err)
    storage.removeItem(STORAGE_KEY)
    return null
  }
}

const writeToStorage = (config: Config) => {
  const storage = getStorage()
  if (!storage) {
    return
  }
  storage.setItem(STORAGE_KEY, JSON.stringify(config))
}

export const readConfig = async (): Promise<Config> => {
  const stored = readFromStorage()
  if (stored) {
    return stored
  }
  writeToStorage(DEFAULT_CONFIG)
  return DEFAULT_CONFIG
}

export const writeConfig = async (config: Config): Promise<Config> => {
  writeToStorage(config)
  return config
}

export const updateConfig = async (
  updates: Partial<Config>,
): Promise<Config> => {
  const current = await readConfig()
  const next = { ...current, ...updates }
  return writeConfig(next)
}
