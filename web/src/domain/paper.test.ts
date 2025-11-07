import { describe, expect, it } from 'vitest'

import { toPaperViewModel } from './paper'
import type { OpenAlexWork } from '../types'

const baseWork: OpenAlexWork = {
  id: 'https://openalex.org/W123',
  doi: '10.1000/xyz123',
  display_name: 'Sample Paper',
  publication_year: 2023,
  abstract_inverted_index: {
    Sample: [0],
    abstract: [1],
    text: [2],
  },
  primary_location: {
    source: {
      display_name: 'Example Journal',
    },
  },
  authorships: [
    {
      author: {
        display_name: 'Alice',
      },
    },
    {
      author: {
        display_name: 'Bob',
      },
    },
  ],
}

describe('toPaperViewModel', () => {
  it('reconstructs the abstract and metadata', () => {
    const model = toPaperViewModel(baseWork)
    expect(model.abstract).toBe('Sample abstract text')
    expect(model.year_journal).toBe('2023 · Example Journal')
    expect(model.authors_joined).toBe('Alice, Bob')
  })

  it('falls back to doi.org link when doi lacks protocol', () => {
    const work: OpenAlexWork = { ...baseWork, doi: '10.1/foo' }
    const model = toPaperViewModel(work)
    expect(model.doi).toBe('https://doi.org/10.1/foo')
  })
})
