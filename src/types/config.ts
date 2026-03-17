export interface Journal {
  name: string
  issn: string
}

export interface Config {
  start_year: number
  end_year: number
  text_size: number
  email: string
  journals: Journal[]
  block_phrases: string[]
}

export const DEFAULT_CONFIG: Config = {
  start_year: 2020,
  end_year: 2025,
  text_size: 16,
  email: '',
  journals: [
    { name: 'QJE', issn: '0033-5533' },
    { name: 'JPE', issn: '0022-3808' },
    { name: 'ECMA', issn: '0012-9682' },
    { name: 'ReStud', issn: '0034-6527' },
    { name: 'AER', issn: '0002-8282' },
  ],
  block_phrases: [
    'front matter',
    'recent referees',
    'back cover',
    'frontmatter',
    'backmatter',
    'turnaround times',
    'forthcoming papers',
    'the econometric society annual reports',
  ],
}
