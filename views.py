from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for, session
import os
import PyPDF2
from werkzeug.utils import secure_filename
import google.generativeai as genai
from pathlib import Path

views = Blueprint("views", __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your_gemini_api_key")
genai.configure(api_key=GEMINI_API_KEY)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

@views.route("/")
def home():
    return render_template('home.html')

@views.route("/api/status")
def api_status():
    status = {
        "status": "true",
        "message": "Server is running",
        "version": "1.0.0"
    }
    return jsonify(status)

@views.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'pdf_file' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)
        
        file = request.files['pdf_file']
        
        # If user does not select file, browser submits an empty part
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                # Create uploads directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Verify file was saved
                if not os.path.exists(filepath):
                    flash(f'Error: File not saved to {filepath}')
                    return redirect(request.url)
                
                # Extract text from PDF
                try:
                    text = extract_text_from_pdf(filepath)
                    
                    # Check if text extraction was successful
                    if not text or len(text) < 10:
                        flash('Warning: Extracted text is very short or empty.')
                    
                    # Save in session for later queries (ensure text is not too large for session)
                    if len(text) > 500000:  # Limit text size for session
                        text = text[:500000] + "... (text truncated due to size)"
                    
                    session.clear()  # Clear any previous session data
                    session['pdf_text'] = text
                    session['pdf_name'] = filename
                    
                    flash('File successfully uploaded and processed!')
                    return redirect(url_for('views.ask_question'))
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

@views.route('/ask', methods=['GET', 'POST'])
def ask_question():
    answer = None
    pdf_name = session.get('pdf_name', None)
    
    if not pdf_name:
        flash('No PDF has been uploaded yet. Please upload a PDF first.')
        return redirect(url_for('views.upload_file'))  # Fixed endpoint reference
    
    if request.method == 'POST':
        question = request.form['question']
        pdf_text = session.get('pdf_text', '')
        
        # Call Gemini API
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Based on the following document, please answer the question.
        Document content: {pdf_text}
        
        Question: {question}

        Note: Respond in plaintext, not markdown.
        """
        
        response = model.generate_content(prompt)
        answer = response.text
    
    return render_template('ask.html', pdf_name=pdf_name, answer=answer)

@views.route('/view_text')
def view_text():
    pdf_name = session.get('pdf_name', None)
    pdf_text = session.get('pdf_text', '')
    
    if not pdf_name:
        flash('No PDF has been uploaded yet. Please upload a PDF first.')
        return redirect(url_for('views.upload_file'))
    
    if not pdf_text:
        flash('No text content found. Please upload a PDF first.')
        return redirect(url_for('views.upload_file'))
    
    # Make sure we're sending plain text, not HTML
    return render_template('view_text.html', pdf_name=pdf_name, pdf_text=pdf_text)

@views.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors within this blueprint"""
    return render_template('404.html'), 404
