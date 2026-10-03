import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from document_tool import extract_pdf

PDF_DIR=Path(__file__).parents[1]/'data'/'supplier_rfps'

def test_all_synthetic_pdfs_have_2_to_4_pages_and_text():
    import fitz
    files=sorted(PDF_DIR.glob('*.pdf'))
    assert len(files)==4
    for path in files:
        doc=fitz.open(path)
        assert 2 <= len(doc) <= 4, f'{path.name} has {len(doc)} pages'
        text=extract_pdf(path)
        for phrase in ['Executive Summary','Implementation','Price','Security','Support']:
            assert phrase.lower() in text.lower(), f'{phrase} missing from {path.name}'
