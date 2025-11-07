import type { Journal, JournalSnapshot } from '../types'

const CROSSREF_BASE =
  import.meta.env.VITE_CROSSREF_BASE ?? 'https://api.crossref.org'

const DEFAULT_ROWS = 200
const REQUEST_TIMEOUT = 45_000

const withTimeout = async <T>(
  factory: (signal: AbortSignal) => Promise<T>,
  timeout = REQUEST_TIMEOUT,
): Promise<T> => {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)
  try {
    return await factory(controller.signal)
  } finally {
    clearTimeout(timer)
  }
}

const buildUrl = (
  journalIssn: string,
  year: number,
  cursor: string,
  email?: string,
) => {
  const startDate = `${year}-01-01`
  const endDate = `${year}-12-31`
  const params = new URLSearchParams({
    filter: `from-pub-date:${startDate},until-pub-date:${endDate}`,
    rows: String(DEFAULT_ROWS),
    cursor,
    select: 'DOI',
  })
  if (email) {
    params.set('mailto', email)
  }
  return `${CROSSREF_BASE}/journals/${journalIssn}/works?${params.toString()}`
}

interface CrossrefWorkItem {
  DOI?: string
}

interface CrossrefResponse {
  status: string
  message?: {
    items?: CrossrefWorkItem[]
    'next-cursor'?: string
  }
}

const fetchPage = async (
  journal: Journal,
  year: number,
  cursor: string,
  email?: string,
) => {
  const response = await withTimeout((signal) =>
    fetch(buildUrl(journal.issn, year, cursor, email), { signal }),
  )
  if (!response.ok) {
    throw new Error(
      `Crossref responded with ${response.status} for ${journal.issn} (${year})`,
    )
  }
  const payload = (await response.json()) as CrossrefResponse
  return payload.message ?? {}
}

export const fetchJournalSnapshot = async (
  journal: Journal,
  year: number,
  email?: string,
): Promise<JournalSnapshot> => {
  const items: CrossrefWorkItem[] = []
  let cursor = '*'
  while (true) {
    const { items: batch = [], 'next-cursor': nextCursor } = await fetchPage(
      journal,
      year,
      cursor,
      email,
    )
    items.push(...batch)
    if (!nextCursor || batch.length === 0) {
      break
    }
    cursor = nextCursor
  }

  return {
    issn: journal.issn,
    name: journal.name,
    year,
    items: items
      .map((item) => (item.DOI ? { DOI: item.DOI } : null))
      .filter((entry): entry is { DOI: string } => Boolean(entry?.DOI)),
  }
}
