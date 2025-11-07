export interface JournalSnapshotItem {
  DOI: string
}

export interface JournalSnapshot {
  issn: string
  name: string
  year: number
  items: JournalSnapshotItem[]
}
