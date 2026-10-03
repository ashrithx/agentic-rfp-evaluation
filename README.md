# Agentic RFP Evaluation & Supplier Ranking

## Project status
This package is aligned to the classroom mini-project brief: document extraction, evidence-grounded LLM evaluation, validation/normalization, deterministic scoring, peer benchmarking, PPI, tie-break ranking, SQLite persistence and Streamlit presentation.

The four synthetic supplier proposals are **3 pages each**, within the required 2–4 page range.

## Architecture
- **Orchestrator/UI:** `app.py`
- **Document Tool:** `document_tool.py` (PyMuPDF)
- **Evaluation Agent:** `llm_evaluator.py` (JSON-capable OpenAI model)
- **Validation Tool:** `validation.py` (custom deterministic normalization)
- **Ranking Tool:** `ranking.py` (deterministic scoring, benchmarks, PPI and tie-breaks)
- **Database:** `database.py`, `setup_db.py`, SQLite
- **Persistence:** `persistence.py`

The LLM judges proposal content only. It does **not** perform final arithmetic, peer benchmarking, tie-breaking or ranking.

## Required formulas
- Absolute weighted score = `SUM((criterion score / maximum score) * criterion weight)`
- Criterion benchmark = highest valid supplier score for that criterion
- Criterion gap = supplier score − benchmark
- Relative performance % = `(supplier score / benchmark) * 100`; safe value 0 when benchmark is zero
- PPI = weighted average of criterion relative-performance percentages
- Tie-break order: higher PPI → earlier submission date → higher historical experience rating → supplier name ascending

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup_db.py
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"
streamlit run app.py
```

## Testing
Run all automated tests:
```bash
python -m pytest -q
```
Expected result in this package:
```text
9 passed
```

The tests cover:
- missing criteria
- malformed scores
- negative/out-of-range scores
- malformed criterion objects
- duplicate criterion IDs
- non-object LLM responses
- absolute score
- benchmark and criterion gap
- relative performance and zero benchmark handling
- PPI
- all ranking tie-break levels
- invalid active weights
- all four synthetic PDFs and their page counts/content

Offline validation demo:
```bash
python demo_validation.py
```
This demonstrates clipping, malformed-score handling, missing criteria and duplicate-criterion warnings without calling an LLM.

## Synthetic supplier proposals
`data/supplier_rfps/` contains four fictional 3-page PDFs:
- **Apex Systems:** strong technical/security; higher price; moderate schedule
- **BrightPath Tech:** lowest price and fastest timeline; weaker compliance/experience evidence
- **NexaWorks:** balanced proposal; strongest implementation governance and support model
- **Orbit Digital:** strong experience/references; less detailed integration plan

No real confidential supplier data is used.

## Sample exported result
`sample_output/rfp_run_result.json` contains a deterministic sample run structure suitable for demonstrating the export format.

## Streamlit screens
The app provides:
1. Active criteria and weights
2. Multiple PDF upload and supplier metadata
3. Evaluation progress
4. Leaderboard
5. Detailed criterion scorecards with evidence, justification, benchmark, gap and relative performance
6. Run ID, validation warnings and tie-break explanation
7. Complete JSON download

## Submission checklist
- [x] Complete source code
- [x] Clear folder structure
- [x] `requirements.txt`
- [x] SQLite creation/seed script
- [x] Four artificial supplier RFP PDFs, 3 pages each
- [x] Evidence-grounded LLM evaluation
- [x] Validation and normalization
- [x] Deterministic scoring/benchmark/PPI/ranking
- [x] Automated tests
- [x] Sample exported JSON
- [x] Offline validation/error demonstration
- [ ] Streamlit Community Cloud public URL — requires deployment from the student's GitHub account
- [ ] Screenshots — capture after local/Cloud run

## Deployment
Push this folder to GitHub and create a Streamlit Community Cloud app using `app.py` as the main file. Add `OPENAI_API_KEY` and optionally `OPENAI_MODEL` under the deployment's Secrets. The database is seeded by running `python setup_db.py` before first use locally; for Cloud, the repository should include the seeded DB or the app can be extended with an initialization check.
