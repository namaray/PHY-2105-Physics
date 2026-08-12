import PyPDF2
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    if not os.path.exists(pdf_path):
        return text
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n"
    return text

# Main execution logic can be placed here to filter according to requirements
