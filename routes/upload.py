from flask import request, render_template, flash, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from pathlib import Path

from router import router
from services.pdf import allowed_file, extract_text_from_pdf

UPLOAD_FOLDER = 'uploads'
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

@router.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            try:
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                if not os.path.exists(filepath):
                    flash(f'Error: File not saved to {filepath}')
                    return redirect(request.url)
                try:
                    text = extract_text_from_pdf(filepath)
                    if not text or len(text) < 10:
                        flash('Warning: Extracted text is very short or empty.')
                    if len(text) > 500000:
                        text = text[:500000] + "... (text truncated due to size)"
                    session.clear()
                    session['pdf_text'] = text
                    session['pdf_name'] = filename
                    flash('File successfully uploaded and processed!')
                    return redirect(url_for('router.ask_question'))
                except Exception as e:
                    flash(f'Error extracting text from PDF: {str(e)}')
                    return redirect(request.url)
            except Exception as e:
                flash(f'Error saving file: {str(e)}')
                return redirect(request.url)
        else:
            flash('File type not allowed. Please upload a PDF.')
            return redirect(request.url)
    return render_template('upload.html')
