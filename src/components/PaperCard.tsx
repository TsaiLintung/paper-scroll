import type { PaperViewModel } from '../types'
import './PaperCard.css'

interface PaperCardProps {
  paper: PaperViewModel
}

export const PaperCard = ({ paper }: PaperCardProps) => {
  return (
    <article className="paper-card">
      <header className="paper-card__header">
        <a
          className="paper-card__title"
          href={paper.doi}
          target="_blank"
          rel="noreferrer"
        >
          {paper.title}
        </a>
        <p className="paper-card__meta">{paper.year_journal}</p>
        <p className="paper-card__meta">{paper.authors_joined}</p>
      </header>
      <p className="paper-card__abstract">{paper.abstract}</p>
    </article>
  )
}
