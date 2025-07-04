import os
from flask import Flask, jsonify, request

from .drive_utils import get_drive_service, list_pdfs, download_file
from .pdf_utils import extract_fields_from_pdf
from .chat_utils import chat_completion

app = Flask(__name__)


@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    folder_id = request.json.get('folder_id')
    if not folder_id:
        return jsonify({'error': 'folder_id required'}), 400
    service = get_drive_service()
    files = list_pdfs(service, folder_id)
    if not files:
        return jsonify({'error': 'no pdf files found'}), 404
    file_id = files[0]['id']
    file_path = download_file(service, file_id, 'downloaded.pdf')
    data = extract_fields_from_pdf(file_path)
    os.remove(file_path)
    return jsonify(data)


@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.json.get('text')
    if not text:
        return jsonify({'error': 'text required'}), 400
    messages = [
        {"role": "system", "content": "Summarize the following text."},
        {"role": "user", "content": text},
    ]
    summary = chat_completion(messages)
    return jsonify({'summary': summary})


@app.route('/chat', methods=['POST'])
def chat():
    messages = request.json.get('messages')
    if not messages:
        return jsonify({'error': 'messages required'}), 400
    reply = chat_completion(messages)
    return jsonify({'reply': reply})


if __name__ == '__main__':
    app.run(debug=True)
