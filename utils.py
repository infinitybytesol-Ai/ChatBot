import PyPDF2  # Replacing fitz (PyMuPDF)

def load_pdf_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def find_relevant_chunks(text, query, window=700):
    lower_text = text.lower()
    lower_query = query.lower()
    index = lower_text.find(lower_query)
    if index == -1:
        return text[:2000]
    start = max(0, index - window)
    end = min(len(text), index + window)
    return text[start:end]
