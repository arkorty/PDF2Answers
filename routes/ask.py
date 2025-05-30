from flask import request, render_template, flash, redirect, url_for, session
from router import router
from services.genai import generate_answer

@router.route('/ask', methods=['GET', 'POST'])
def ask_question():
    answer = None
    pdf_name = session.get('pdf_name', None)
    if not pdf_name:
        flash('No PDF has been uploaded yet. Please upload a PDF first.')
        return redirect(url_for('router.upload_file'))
    if request.method == 'POST':
        question = request.form['question']
        pdf_text = session.get('pdf_text', '')
        answer = generate_answer(pdf_text, question)
    return render_template('ask.html', pdf_name=pdf_name, answer=answer)
