import io
from typing import List, Dict
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')


def get_drive_service():
    """Return an authenticated Google Drive service using a service account."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    service = build('drive', 'v3', credentials=creds)
    return service


def list_pdfs(service, folder_id: str) -> List[Dict[str, str]]:
    """List PDF files in a given Google Drive folder."""
    query = f"'{folder_id}' in parents and mimeType='application/pdf'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])


def download_file(service, file_id: str, file_path: str) -> str:
    """Download a file from Google Drive to the local filesystem."""
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.close()
    return file_path
