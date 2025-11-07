import type { OpenAlexWork } from '../types'

const OPENALEX_BASE =
  import.meta.env.VITE_OPENALEX_BASE ?? 'https://api.openalex.org'

const sanitizeDoi = (doi: string) => {
  const trimmed = doi.trim()
  const normalized = trimmed.startsWith('http')
    ? trimmed
    : `https://doi.org/${trimmed}`
  return normalized.toLowerCase()
}

export const fetchOpenAlexWork = async (
  doi: string,
  email?: string,
): Promise<OpenAlexWork> => {
  const doiUrl = sanitizeDoi(doi)
  const params = new URLSearchParams()
  if (email) {
    params.set('mailto', email)
  }
  const url = `${OPENALEX_BASE}/works/${encodeURIComponent(doiUrl)}${
    params.size ? `?${params.toString()}` : ''
  }`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`OpenAlex request failed (${response.status}) for ${doi}`)
  }
  return (await response.json()) as OpenAlexWork
}
