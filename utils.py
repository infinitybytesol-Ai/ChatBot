import fitz  # PyMuPDF

def load_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def find_relevant_chunks(text, query, window=700):
    lower_text = text.lower()
    lower_query = query.lower()
    index = lower_text.find(lower_query)
    if index == -1:
        return text[:2000]
    start = max(0, index - window)
    end = min(len(text), index + window)
    return text[start:end]
