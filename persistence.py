import json, secrets
from datetime import datetime
from database import connect

def persist_run(results, warnings):
    run_id = datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + secrets.token_hex(3)
    with connect() as conn:
        conn.execute('INSERT INTO rfp_runs (rfp_run_id, created_at, status) VALUES (?, ?, ?)',
                     (run_id, datetime.now().isoformat(timespec='seconds'), 'completed'))
        for s in results:
            result_json = json.dumps(s, ensure_ascii=False)
            conn.execute('''INSERT INTO supplier_results
                (rfp_run_id, supplier_name, submission_date, experience_rating,
                 absolute_score, ppi, final_rank, result_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (run_id, s['supplier_name'], s['submission_date'], s['experience_rating'],
                 s['absolute_score'], s['ppi'], s['final_rank'], result_json))
    return run_id
