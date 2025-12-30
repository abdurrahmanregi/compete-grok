from langchain_core.tools import tool
import os
import base64
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
import re
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env")
client = Mistral(api_key=api_key)

logger = logging.getLogger(__name__)

@tool
def convert_pdf_url(url: str) -> dict:
    """Convert a PDF from a URL to Markdown using Mistral OCR API directly."""
    try:
        # Set up session with retries
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Download PDF
        response = session.get(url)
        if response.status_code == 403:
            # Extract basic metadata
            title_match = re.search(r'/([^/]+\.pdf)$', url)
            title = title_match.group(1) if title_match else "Unknown"
            return {
                "success": False,
                "error": "403 Forbidden",
                "details": {
                    "url": url,
                    "title": title,
                    "reason": "Access denied by server"
                }
            }
        response.raise_for_status()
        pdf_content = response.content

        # Encode to base64
        base64_encoded = base64.b64encode(pdf_content).decode('utf-8')

        # Create data URI
        data_uri = f"data:application/pdf;base64,{base64_encoded}"

        # Call OCR
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": data_uri
            },
            table_format="markdown"
        )
        md_pages = [page.markdown for page in ocr_response.pages]
        md_content = "\n\n---\n\n".join(md_pages)
        return {"success": True, "content": md_content}
    except Exception as e:
        logger.error(f"OCR error in convert_pdf_url: {e}")
        raise ValueError(f"OCR error for {url}: {str(e)}")