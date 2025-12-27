from langchain_core.tools import tool
import os
import base64
import requests
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env")
client = Mistral(api_key=api_key)

@tool
def convert_pdf_url(url: str) -> str:
    """Convert a PDF from a URL to Markdown using Mistral OCR API directly."""
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        pdf_bytes = response.content
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
    except requests.RequestException as e:
        return f"Download error for {url}: {str(e)}"
    except Exception as e:
        return f"OCR error for {url}: {str(e)}"