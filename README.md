## PaperScroll

PaperScroll is a minimalist React + Vite app that samples fresh papers from [OpenAlex](https://openalex.org/) for the journals you care about. Configure a year window (2020–2025 by default), pick your favorite economics journals, and scroll—new cards stream in automatically while preferences stay local to the browser.

### Quick Start
```bash
npm install
npm run dev
```

### Key Features
- Randomized feed powered by the OpenAlex `sample=1` API.
- Settings drawer with journal management, year bounds.
- Local persistence via `localStorage`; no accounts or servers needed.

Need contribution/setup specifics? See `AGENTS.md` and `SPEC.md`.
