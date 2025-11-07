export interface OpenAlexAuthorRef {
  display_name: string
}

export interface OpenAlexAuthor {
  author: OpenAlexAuthorRef
}

export interface OpenAlexSource {
  display_name?: string
}

export interface OpenAlexPrimaryLocation {
  source?: OpenAlexSource
}

export interface OpenAlexWork {
  id: string
  doi?: string
  display_name?: string
  title?: string
  publication_year?: number
  abstract_inverted_index?: Record<string, number[]>
  primary_location?: OpenAlexPrimaryLocation
  authorships?: OpenAlexAuthor[]
}

export interface PaperViewModel {
  id: string
  doi: string
  title: string
  abstract: string
  year_journal: string
  authors_joined: string
  raw: OpenAlexWork
}

export interface PaperRecord {
  doi: string
  payload: OpenAlexWork
}
