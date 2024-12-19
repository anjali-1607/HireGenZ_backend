from pdfminer.high_level import extract_text
from io import BytesIO


def parse_resume(file):
    """
    Extract text content from a PDF resume file.
    """
    try:
        # Convert the InMemoryUploadedFile to a file-like object (BytesIO)
        file_content = BytesIO(file.read())
        
        # Extract text from the PDF content
        content = extract_text(file_content)
        
        return content
    except Exception as e:
        raise ValueError(f"Error extracting text from resume: {str(e)}")
