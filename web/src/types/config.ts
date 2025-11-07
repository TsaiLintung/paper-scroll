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
}

export const DEFAULT_CONFIG: Config = {
  start_year: 2021,
  end_year: 2021,
  text_size: 16,
  email: '',
  journals: [
    { name: 'aer', issn: '0002-8282' },
  ],
}
