import json
from datetime import date
from pathlib import Path
import streamlit as st

from database import DB_PATH, load_active_criteria, validate_active_weights
from setup_db import initialize_database
from document_tool import extract_pdf
from llm_evaluator import evaluate_with_llm
from persistence import persist_run
from ranking import calculate_results
from validation import validate_and_normalize

st.set_page_config(page_title='Agentic RFP Evaluation', layout='wide')
st.title('🤖 Agentic RFP Evaluation & Supplier Ranking')
st.caption('LLM judges proposal content; deterministic Python validates results and performs all formulas, benchmarking and ranking.')

if not DB_PATH.exists():
    initialize_database(reset=False)

try:
    criteria = load_active_criteria()
    validate_active_weights(criteria)
except Exception as exc:
    st.error(str(exc)); st.stop()

with st.sidebar:
    st.header('Active Criteria')
    st.table([{'Criterion': c['name'], 'Weight %': c['weight'], 'Max': c['max_score']} for c in criteria])
    st.caption(f"Total active weight: {sum(float(c['weight']) for c in criteria):.0f}%")

uploads = st.file_uploader('Upload supplier RFP PDFs', type=['pdf'], accept_multiple_files=True)

if uploads:
    st.subheader('Supplier Metadata')
    metadata = {}
    for i, f in enumerate(uploads):
        with st.expander(f'📄 {f.name}', expanded=True):
            default_name = Path(f.name).stem.replace('_', ' ')
            name = st.text_input('Supplier name', default_name, key=f'name_{i}')
            sub_date = st.date_input('Submission date', value=date.today(), key=f'date_{i}')
            exp = st.number_input('Historical experience rating (0-10)', 0.0, 10.0, 5.0, 0.5, key=f'exp_{i}')
            metadata[f.name] = {'supplier_name': name.strip(), 'submission_date': str(sub_date), 'experience_rating': float(exp)}

    if st.button('🚀 Evaluate Suppliers', type='primary'):
        # Reload immediately before evaluation to satisfy the required architecture.
        criteria = load_active_criteria()
        validate_active_weights(criteria)
        all_results, all_warnings = [], []
        progress = st.progress(0)
        for idx, f in enumerate(uploads):
            supplier = metadata[f.name]
            with st.status(f"Evaluating {supplier['supplier_name']}...", expanded=False):
                text = extract_pdf(f.getvalue())
                if not text:
                    raise ValueError(f'No text could be extracted from {f.name}.')
                raw = evaluate_with_llm(supplier['supplier_name'], text, criteria)
                normalized, warnings = validate_and_normalize(raw, criteria, supplier['supplier_name'])
                by_id = {x['criterion_id']: x for x in normalized}
                all_results.append({**supplier, 'criteria': by_id,
                    'risks': raw.get('risks', []) if isinstance(raw, dict) else [],
                    'overall_summary': raw.get('overall_summary', '') if isinstance(raw, dict) else ''})
                all_warnings.extend([f"{supplier['supplier_name']}: {w}" for w in warnings])
            progress.progress((idx + 1) / len(uploads))

        results, benchmarks = calculate_results(all_results, criteria)
        run_id = persist_run(results, all_warnings)
        st.session_state.update(results=results, warnings=all_warnings, run_id=run_id, benchmarks=benchmarks)

if 'results' in st.session_state:
    results = st.session_state['results']
    st.success(f"Completed run: {st.session_state['run_id']}")
    st.subheader('🏆 Leaderboard')
    st.dataframe([{
        'Rank': s['final_rank'], 'Supplier': s['supplier_name'],
        'Absolute Score': round(s['absolute_score'], 2), 'PPI %': round(s['ppi'], 2),
        'Submission Date': s['submission_date'], 'Experience': s['experience_rating']
    } for s in results], use_container_width=True, hide_index=True)

    st.subheader('Detailed Scorecards')
    for s in results:
        with st.expander(f"Rank {s['final_rank']} — {s['supplier_name']}"):
            st.write(f"**Absolute weighted score:** {s['absolute_score']:.2f} / 100")
            st.write(f"**PPI:** {s['ppi']:.2f}%")
            st.dataframe(s['details'], use_container_width=True, hide_index=True)
            if s.get('risks'): st.warning('Risks: ' + '; '.join(s['risks']))
            if s.get('overall_summary'): st.info(s['overall_summary'])

    st.subheader('Run Details')
    st.code(st.session_state['run_id'])
    st.markdown('**Mandatory tie-break order:** higher PPI → earlier submission date → higher historical experience rating → supplier name ascending.')
    if st.session_state['warnings']:
        st.warning('Validation warnings')
        for w in st.session_state['warnings']: st.write('• ' + w)
    else:
        st.success('No validation warnings.')

    export = {'rfp_run_id': st.session_state['run_id'], 'results': results, 'warnings': st.session_state['warnings']}
    st.download_button('⬇️ Download complete JSON', json.dumps(export, indent=2, ensure_ascii=False),
                       file_name=f"{st.session_state['run_id']}.json", mime='application/json')
