# Robert Leggieri | Applied AI & NLP Development

Personal portfolio for [rjleggieri.github.io](https://rjleggieri.github.io), featuring selected public work and public-safe summaries of graduate projects completed in the M.S. Artificial Intelligence program at The University of Texas at Austin.

## Local development

```bash
pnpm install
pnpm run dev
```

## Production build

```bash
pnpm run build
```

The site is a static Vite build. GitHub Pages can publish the generated `dist` directory through a Pages workflow or the project can be deployed directly from source with a compatible static hosting provider.

The project pages in `projects/` are registered as Vite build inputs. The former
evaluation URL redirects to the evaluation section of the unified text–prosody case study. Core content and links remain usable without JavaScript.

## Documents

The editable document sources are `scripts/generate_resume.py` and
`scripts/generate_nli_report.py`. Install the build dependencies with
`python -m pip install -r scripts/requirements-documents.txt`, then run:

```bash
python scripts/generate_resume.py
python scripts/generate_nli_report.py
python scripts/validate_documents.py
```

Both generators update the copies under `docs/`, `public/docs/`, and `output/pdf/`.
The NLI paper presents the study as a standalone manuscript, with methods,
results, discussion, limitations, and verified references. The document validator
checks the experimental values and figure against the archived course artifact
under `docs/archive/` and checks consistency of all published PDF copies.

## Academic work

Some projects were completed in private course repositories. This portfolio describes the problem, approach, and results without distributing restricted starter code, assignment materials, or private implementations.
