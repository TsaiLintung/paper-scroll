import { openDB, type DBSchema, type IDBPDatabase } from 'idb'

import type {
  Config,
  JournalSnapshot,
  PaperRecord,
  StatusPayload,
} from '../types'
import { DEFAULT_CONFIG } from '../types'

interface PaperScrollDB extends DBSchema {
  config: {
    key: string
    value: Config
  }
  journalSnapshots: {
    key: string
    value: JournalSnapshot
  }
  status: {
    key: string
    value: StatusPayload
  }
  papers: {
    key: string
    value: PaperRecord
  }
}

const DB_NAME = 'paper-scroll'
const DB_VERSION = 1
const CONFIG_KEY = 'singleton'

let dbPromise: Promise<IDBPDatabase<PaperScrollDB>> | null = null

const makeSnapshotKey = (name: string, year: number) => `${name}-${year}`

const initDb = () =>
  openDB<PaperScrollDB>(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('config')) {
        db.createObjectStore('config')
      }
      if (!db.objectStoreNames.contains('journalSnapshots')) {
        db.createObjectStore('journalSnapshots')
      }
      if (!db.objectStoreNames.contains('status')) {
        db.createObjectStore('status')
      }
      if (!db.objectStoreNames.contains('papers')) {
        db.createObjectStore('papers')
      }
    },
  })

const getDb = () => {
  if (!dbPromise) {
    dbPromise = initDb()
  }
  return dbPromise
}

export const readConfig = async (): Promise<Config> => {
  const db = await getDb()
  const config = await db.get('config', CONFIG_KEY)
  if (config) {
    return config
  }
  await db.put('config', DEFAULT_CONFIG, CONFIG_KEY)
  return DEFAULT_CONFIG
}

export const writeConfig = async (config: Config): Promise<Config> => {
  const db = await getDb()
  await db.put('config', config, CONFIG_KEY)
  return config
}

export const updateConfig = async (
  updates: Partial<Config>,
): Promise<Config> => {
  const current = await readConfig()
  const next = { ...current, ...updates }
  return writeConfig(next)
}

export const saveJournalSnapshot = async (
  snapshot: JournalSnapshot,
): Promise<void> => {
  const db = await getDb()
  await db.put(
    'journalSnapshots',
    snapshot,
    makeSnapshotKey(snapshot.name, snapshot.year),
  )
}

export const listJournalSnapshots = async (): Promise<JournalSnapshot[]> => {
  const db = await getDb()
  return db.getAll('journalSnapshots')
}

export const writeStatus = async (payload: StatusPayload): Promise<void> => {
  const db = await getDb()
  await db.put('status', payload, CONFIG_KEY)
}

export const readStatus = async (): Promise<StatusPayload | undefined> => {
  const db = await getDb()
  return db.get('status', CONFIG_KEY)
}

export const cachePaper = async (record: PaperRecord): Promise<void> => {
  const db = await getDb()
  await db.put('papers', record, record.doi)
}

export const getCachedPaper = async (
  doi: string,
): Promise<PaperRecord | undefined> => {
  const db = await getDb()
  return db.get('papers', doi)
}
