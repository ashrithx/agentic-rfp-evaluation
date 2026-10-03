import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'data' / 'rfp_evaluation.db'

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_active_criteria():
    with connect() as conn:
        return conn.execute('''
            SELECT criterion_id, name, description, weight, max_score
            FROM evaluation_criteria WHERE is_active=1 ORDER BY criterion_id
        ''').fetchall()

def validate_active_weights(criteria):
    total = sum(float(c['weight']) for c in criteria)
    if abs(total - 100.0) > 1e-9:
        raise ValueError(f'Active criterion weights must total 100%; current total is {total:.2f}%.')
    if any(float(c['max_score']) <= 0 for c in criteria):
        raise ValueError('Every active criterion must have max_score > 0.')
