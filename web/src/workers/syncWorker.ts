/// <reference lib="webworker" />

import { fetchJournalSnapshot } from '../services/crossref'
import type {
  Journal,
  SyncWorkerInboundMessage,
  SyncWorkerOutboundMessage,
} from '../types'

declare const self: DedicatedWorkerGlobalScope

const postMessageToMain = (message: SyncWorkerOutboundMessage) => {
  self.postMessage(message)
}

const postStatus = (message: string, progress: number) => {
  postMessageToMain({
    type: 'status',
    payload: { message, progress },
  })
}

const postError = (message: string) => {
  postMessageToMain({
    type: 'error',
    message,
  })
}

const iterateTargets = (journals: Journal[], start: number, end: number) => {
  const targets: Array<{ journal: Journal; year: number }> = []
  journals.forEach((journal) => {
    for (let year = start; year <= end; year += 1) {
      targets.push({ journal, year })
    }
  })
  return targets
}

let isRunning = false

self.onmessage = async (event: MessageEvent<SyncWorkerInboundMessage>) => {
  const { data } = event
  if (data?.type !== 'start') {
    return
  }
  if (isRunning) {
    postError('Sync already running.')
    return
  }
  isRunning = true
  try {
    const { journals, start_year, end_year, email } = data.payload
    const targets = iterateTargets(journals, start_year, end_year)
    if (targets.length === 0) {
      postStatus('No journals configured.', 1)
      postMessageToMain({ type: 'done' })
      return
    }
    for (let index = 0; index < targets.length; index += 1) {
      const { journal, year } = targets[index]
      postStatus(`Fetching ${journal.name} (${year})`, index / targets.length)
      try {
        const snapshot = await fetchJournalSnapshot(journal, year, email)
        postMessageToMain({ type: 'snapshot', payload: snapshot })
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : `Failed to fetch ${journal.name} (${year})`
        postError(message)
        postStatus(message, 0)
        postMessageToMain({ type: 'done' })
        return
      }
    }
    postStatus('All journals updated.', 1)
    postMessageToMain({ type: 'done' })
  } finally {
    isRunning = false
  }
}
