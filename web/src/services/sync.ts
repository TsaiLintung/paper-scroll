import { DataStore } from '../data/store'
import type { JournalSnapshot, StatusPayload } from '../types'

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export class SyncService {
  private isRunning = false
  private store: DataStore

  constructor(store: DataStore) {
    this.store = store
  }

  async startSync(): Promise<void> {
    if (this.isRunning) {
      return
    }
    this.isRunning = true
    await this.updateStatus({ message: 'Sync started…', progress: 0 })
    try {
      await this.simulateFetch()
      await this.updateStatus({ message: 'All journals updated.', progress: 1 })
    } finally {
      this.isRunning = false
    }
  }

  private async simulateFetch(): Promise<void> {
    const steps = [
      { message: 'Fetching journals…', progress: 0.35 },
      { message: 'Indexing papers…', progress: 0.7 },
    ]

    for (const step of steps) {
      await sleep(600)
      await this.updateStatus(step)
    }

    const snapshot: JournalSnapshot = {
      issn: '0002-8282',
      name: 'aer',
      year: 2021,
      items: [{ DOI: '10.1038/s41586-020-2649-2' }],
    }
    await this.store.saveSnapshot(snapshot)
  }

  private async updateStatus(payload: StatusPayload) {
    await this.store.saveStatus(payload)
  }
}
