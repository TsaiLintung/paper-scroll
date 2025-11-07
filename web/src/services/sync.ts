import type {
  Config,
  SyncWorkerOutboundMessage,
  SyncWorkerInboundMessage,
} from '../types'
import { DataStore } from '../data/store'

type Resolve = () => void
type Reject = (error: Error) => void

export class SyncService {
  private worker: Worker

  private pending: Promise<void> | null = null

  private store: DataStore

  constructor(store: DataStore) {
    this.store = store
    this.worker = new Worker(
      new URL('../workers/syncWorker.ts', import.meta.url),
      { type: 'module' },
    )
  }

  start(config: Config): Promise<void> {
    if (this.pending) {
      return this.pending
    }

    this.pending = new Promise<void>((resolve, reject) => {
      const handleMessage = (event: MessageEvent<SyncWorkerOutboundMessage>) =>
        this.handleWorkerMessage(event, resolve, reject, cleanup)
      const handleError = (event: ErrorEvent) => {
        cleanup()
        reject(event.error ?? new Error(event.message))
      }

      const cleanup = () => {
        this.worker.removeEventListener('message', handleMessage)
        this.worker.removeEventListener('error', handleError)
        this.pending = null
      }

      this.worker.addEventListener('message', handleMessage)
      this.worker.addEventListener('error', handleError)

      const payload: SyncWorkerInboundMessage = {
        type: 'start',
        payload: {
          journals: config.journals,
          start_year: config.start_year,
          end_year: config.end_year,
          email: config.email,
        },
      }
      this.worker.postMessage(payload)
    })

    return this.pending
  }

  dispose() {
    this.worker.terminate()
  }

  private async handleWorkerMessage(
    event: MessageEvent<SyncWorkerOutboundMessage>,
    resolve: Resolve,
    reject: Reject,
    cleanup: () => void,
  ) {
    const { data } = event
    switch (data.type) {
      case 'status':
        await this.store.saveStatus(data.payload)
        break
      case 'snapshot':
        await this.store.saveSnapshot(data.payload)
        break
      case 'error':
        await this.store.saveStatus({ message: data.message, progress: 0 })
        cleanup()
        reject(new Error(data.message))
        return
      case 'done':
        cleanup()
        resolve()
        return
      default:
        break
    }
  }
}
