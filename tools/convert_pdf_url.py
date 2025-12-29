from langchain_core.tools import tool
import os
import base64
import requests
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
def convert_pdf_url(url: str) -> str:
    """Convert a PDF from a URL to Markdown using Mistral OCR API directly."""
    try:
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": url
            },
            table_format="markdown"
        )
        md_pages = [page.markdown for page in ocr_response.pages]
        md_content = "\n\n---\n\n".join(md_pages)
        return md_content
    except Exception as e:
        logger.error(f"OCR error in convert_pdf_url: {e}")  # Log API or processing errors for debugging
        return f"OCR error for {url}: {str(e)}"