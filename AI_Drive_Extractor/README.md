# AI Drive Extractor

This project demonstrates a minimal integration between Google Drive, PDF parsing and OpenAI's GPT API. It exposes simple Flask endpoints that:

1. Fetch a PDF from a specified Google Drive folder using a service account.
2. Extract fields from the PDF with `pdfplumber`.
3. Send text to GPT-4 for summarization or chat responses.

Credentials for Google Drive and OpenAI are read from environment variables. See `requirements.txt` for dependencies.
