from pathlib import Path
import fitz

def extract_pdf(path_or_bytes):
    if isinstance(path_or_bytes, (str, Path)):
        doc = fitz.open(path_or_bytes)
    else:
        doc = fitz.open(stream=path_or_bytes, filetype='pdf')
    try:
        text = '\n'.join(page.get_text('text') for page in doc).strip()
        return text
    finally:
        doc.close()
