import type { OpenAlexWork, PaperViewModel } from '../types'

const DEFAULT_DOI = '10.1038/s41586-020-2649-2'

const toDoiUrl = (doi?: string) => {
  if (!doi) {
    return ''
  }
  return doi.startsWith('http') ? doi : `https://doi.org/${doi}`
}

const reconstructAbstract = (index?: Record<string, number[]>) => {
  if (!index) {
    return ''
  }
  const tokens: Array<{ pos: number; word: string }> = []
  Object.entries(index).forEach(([word, positions]) => {
    positions.forEach((pos) => tokens.push({ pos, word }))
  })
  tokens.sort((a, b) => a.pos - b.pos)
  return tokens.map((entry) => entry.word).join(' ')
}

const formatYearJournal = (work: OpenAlexWork) => {
  const year = work.publication_year
  const journal = work.primary_location?.source?.display_name ?? ''
  if (!year || !journal) {
    return ''
  }
  return `${year} · ${journal}`
}

const joinAuthors = (work: OpenAlexWork) => {
  const authors = work.authorships ?? []
  return authors
    .map((authorship) => authorship.author?.display_name)
    .filter(Boolean)
    .join(', ')
}

export const toPaperViewModel = (work: OpenAlexWork): PaperViewModel => {
  const doiUrl = toDoiUrl(work.doi ?? DEFAULT_DOI)
  const title = work.display_name ?? work.title ?? 'Untitled'
  const abstract = reconstructAbstract(work.abstract_inverted_index)
  const yearJournal = formatYearJournal(work)
  const authorsJoined = joinAuthors(work)

  return {
    id: work.id,
    doi: doiUrl,
    title,
    abstract,
    year_journal: yearJournal,
    authors_joined: authorsJoined,
    raw: work,
  }
}
