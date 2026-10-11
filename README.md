<<<<<<< HEAD
# Casino Bonus Scraper — Screening Task

A small Python scraper and responsive web page that displays three casino bonus records from one public comparison page. The script extracts the source text itself and asks an LLM to normalize the fields; it does not manually seed the offers.

## Stack

- Python 3.10+
- `requests` and `BeautifulSoup` for fetching/parsing public HTML
- OpenAI API (`gpt-4o-mini` by default) for free-text normalization
- HTML, CSS and vanilla JavaScript for the responsive page
- JSON as the data interchange format

## Source and scraping etiquette

Default source: <https://betproof.co.za/casino-bonuses-south-africa/sign-up-bonus-south-africa/>

Before running, the script fetches the source's `robots.txt` and stops if it cannot verify permission or if the path is disallowed. If access is denied or blocked, choose another public source that permits automated access. Do not bypass logins, CAPTCHAs, or blocks. The source page can change; the script deliberately fails instead of inventing records if it cannot find the expected rows.

## Install and run

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Provide your key either in the shell or in a local `.env` file (copy `.env.example`; `.env` is git-ignored and is loaded automatically):

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY="your-key-here"
python scraper.py
```

```bash
# macOS/Linux
export OPENAI_API_KEY="your-key-here"
python scraper.py
```

Optional settings: `OPENAI_MODEL`, `SOURCE_URL`, and `SCRAPER_CONTACT` (your email, included in the User-Agent so site owners can reach you). Output is written to `data/bonuses.json`.

### Useful flags

| Flag | Purpose |
| --- | --- |
| `--html-file page.html` | Parse a saved copy of the page instead of fetching it (debug selectors offline) |
| `--no-llm` | Skip the LLM and keep raw text; no API key needed (debugging only, wagering is left null) |
| `--output path.json` | Write somewhere other than `data/bonuses.json` |
| `-v` | Verbose logging |

### Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use a synthetic fixture (`tests/fixtures/sample_page.html`) and a fake LLM client, so they need no network or API key.

### What the scraper guards against

- **Robots.txt**: fails closed (404/410 = no rules; 401/403 or unreachable = stop).
- **Fetch failures**: retries with exponential backoff on network errors, 429 and 5xx.
- **Markup drift**: columns are located by header text, not position; if any of the three target rows is missing, nothing is written and the previous `bonuses.json` stays live.
- **LLM mistakes**: the output must contain all schema keys, extra keys are dropped, `source_url` is always set by the scraper, and a wagering multiplier that does not appear in the scraped text is set to null.
- **Partial writes**: output is written to a temp file then renamed.

## Preview the website locally

The site lives in the project root (`index.html`, `styles.css`, `app.js`) and reads `data/bonuses.json`:

```bash
python -m http.server 8000
```

Open <http://localhost:8000/>. Column headers are click-sortable, and a warning banner appears if the data is more than 7 days old.

To publish on GitHub Pages or any static host, serve the repository root (it must include `data/bonuses.json`).

## Scheduled updates

`.github/workflows/scrape.yml` runs the tests and the scraper daily and commits `data/bonuses.json` if it changed. Add `OPENAI_API_KEY` as a repository secret (and optionally `SCRAPER_CONTACT` as a repository variable).

## Data schema

Each record contains `casino_name`, `welcome_bonus`, `wagering_requirement` (number or null), `minimum_deposit` (string or null), and `source_url`. The source URL is kept by the scraper and is not entrusted to the LLM. If the source has multiple wagering conditions, the LLM should return null rather than guessing a single multiplier.

## Limitations and production considerations

- The source's current `robots.txt` and markup must be verified from the machine running the scraper; the development sandbox had no outbound access to the source, so a successful live scrape has not been verified. The parser is covered by tests against a synthetic fixture only; run `python scraper.py` once and check the output against the live page.
- An API key and API usage are required for LLM normalization.
- For production, use a scheduler, retries with backoff, structured logs, alerts, schema validation, and human review for ambiguous terms. Keep historical snapshots and source timestamps to audit changes.
- This is an assessment prototype, not gambling advice. Offers change; verify current terms directly with operators. 18+ only; gamble responsibly.
=======
# casino-bonus-scrape
>>>>>>> cf909d201cbf6897c44ea457ad5b01c4f6a9278e
