#!/usr/bin/env python3
"""Test script for convert_pdf_url tool."""

from tools.convert_pdf_url import convert_pdf_url

# Test with a valid PDF URL
url = "https://arxiv.org/pdf/2201.04234"  # Example PDF
try:
    result = convert_pdf_url(url)
    print("Success:", len(result), "characters")
    print("First 200 chars:", result[:200])
except Exception as e:
    print("Error:", e)