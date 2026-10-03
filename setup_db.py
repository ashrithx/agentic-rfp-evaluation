import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parent / 'data' / 'rfp_evaluation.db'

def initialize_database(reset=False):
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as conn:
        if reset:
            conn.executescript('DROP TABLE IF EXISTS supplier_results; DROP TABLE IF EXISTS rfp_runs; DROP TABLE IF EXISTS evaluation_criteria;')
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS evaluation_criteria (
            criterion_id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL,
            weight REAL NOT NULL, max_score REAL NOT NULL, is_active INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS rfp_runs (
            rfp_run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS supplier_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT, rfp_run_id TEXT NOT NULL,
            supplier_name TEXT NOT NULL, submission_date TEXT NOT NULL,
            experience_rating REAL NOT NULL, absolute_score REAL NOT NULL, ppi REAL NOT NULL,
            final_rank INTEGER NOT NULL, result_json TEXT NOT NULL,
            FOREIGN KEY(rfp_run_id) REFERENCES rfp_runs(rfp_run_id));
        ''')
        count=conn.execute('SELECT COUNT(*) FROM evaluation_criteria').fetchone()[0]
        if count == 0:
            conn.executemany('''INSERT INTO evaluation_criteria
                (criterion_id,name,description,weight,max_score,is_active) VALUES (?,?,?,?,?,?)''', [
                (1,'Technical Capability','Architecture, integrations, scalability, technical fit',30,10,1),
                (2,'Implementation Plan','Timeline, milestones, staffing, risk plan',20,10,1),
                (3,'Commercial Value','Pricing clarity, total cost, assumptions',20,10,1),
                (4,'Security & Compliance','Controls, certifications, privacy, auditability',20,10,1),
                (5,'Support & Experience','Support model, similar projects, references',10,10,1)])
    return DB

if __name__ == '__main__':
    print(f'Created/verified {initialize_database(reset=True)}')
