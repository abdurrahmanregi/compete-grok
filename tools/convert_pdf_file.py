from langchain_core.tools import tool
import os
import base64
import logging
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env")
client = Mistral(api_key=api_key)

logger = logging.getLogger(__name__)

@tool
def convert_pdf_file(file_path: str) -> str:
    """Convert a local PDF file to Markdown using Mistral OCR API directly."""
    try:
        if not os.path.isfile(file_path):
            return f"File not found or not a file: {file_path}"
        with open(file_path, 'rb') as f:
            pdf_bytes = f.read()
        if not pdf_bytes.startswith(b'%PDF'):
            return f"Invalid PDF file: {file_path}"
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{b64_pdf}"
            },
            table_format="markdown"
        )
        md_pages = [page.markdown for page in ocr_response.pages]
        md_content = "\n\n---\n\n".join(md_pages)
        return md_content
    except Exception as e:
        logger.error(f"OCR error in convert_pdf_file: {e}")  # Log file or API errors for debugging
        return f"OCR error for {file_path}: {str(e)}"