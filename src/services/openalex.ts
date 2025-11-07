import type { OpenAlexWork } from '../types'

const OPENALEX_BASE =
  import.meta.env.VITE_OPENALEX_BASE ?? 'https://api.openalex.org'
const DEFAULT_INTERVAL_MS = 1000
const POLITE_INTERVAL_MS = 200
const MAX_ATTEMPTS = 5
const RETRYABLE_STATUSES = new Set([403, 429, 500, 502, 503])

const delay = (ms: number) =>
  new Promise<void>((resolve) => {
    setTimeout(resolve, ms)
  })

let lastRequestTimestamp = 0
let rateLimiter: Promise<void> = Promise.resolve()

const getInterval = (email?: string) => {
  if (email && email.trim().length > 0) {
    return POLITE_INTERVAL_MS
  }
  return DEFAULT_INTERVAL_MS
}

const scheduleRequest = (interval: number) => {
  rateLimiter = rateLimiter.then(async () => {
    const now = Date.now()
    const wait = Math.max(0, lastRequestTimestamp + interval - now)
    if (wait > 0) {
      await delay(wait)
    }
    lastRequestTimestamp = Date.now()
  })
  return rateLimiter
}

const randomSeed = () => String(Math.floor(Math.random() * 1_000_000_000))

interface SampleWorkParams {
  issn: string
  year: number
  email?: string
}

interface OpenAlexResponse {
  results?: OpenAlexWork[]
}

export const sampleOpenAlexWork = async ({
  issn,
  year,
  email,
}: SampleWorkParams): Promise<OpenAlexWork> => {
  const interval = getInterval(email)
  const params = new URLSearchParams({
    filter: [
      `primary_location.source.issn:${issn}`,
      `from_publication_date:${year}-01-01`,
      `to_publication_date:${year}-12-31`,
    ].join(','),
    sample: '1',
    'per-page': '1',
    seed: randomSeed(),
  })
  if (email) {
    params.set('mailto', email.trim())
  }
  const url = `${OPENALEX_BASE}/works?${params.toString()}`

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    await scheduleRequest(interval)
    const response = await fetch(url)
    if (response.ok) {
      const payload = (await response.json()) as OpenAlexResponse
      const work = payload.results?.[0]
      if (!work) {
        throw new Error(`No papers available for ${issn} (${year}) right now.`)
      }
      return work
    }

    if (RETRYABLE_STATUSES.has(response.status) && attempt < MAX_ATTEMPTS) {
      const backoff = Math.min(1000 * 2 ** (attempt - 1), 8000)
      await delay(backoff)
      continue
    }

    throw new Error(
      `OpenAlex sampling failed (${response.status}) for ${issn} (${year})`,
    )
  }

  throw new Error(`OpenAlex sampling gave up for ${issn} (${year}).`)
}
