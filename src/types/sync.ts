import type { Config, JournalSnapshot, StatusPayload } from './index'

export type SyncWorkerStartMessage = {
  type: 'start'
  payload: Pick<Config, 'journals' | 'start_year' | 'end_year' | 'email'>
}

export type SyncWorkerStatusMessage = {
  type: 'status'
  payload: StatusPayload
}

export type SyncWorkerSnapshotMessage = {
  type: 'snapshot'
  payload: JournalSnapshot
}

export type SyncWorkerDoneMessage = {
  type: 'done'
}

export type SyncWorkerErrorMessage = {
  type: 'error'
  message: string
}

export type SyncWorkerOutboundMessage =
  | SyncWorkerStatusMessage
  | SyncWorkerSnapshotMessage
  | SyncWorkerDoneMessage
  | SyncWorkerErrorMessage

export type SyncWorkerInboundMessage = SyncWorkerStartMessage
