from flask import render_template, flash, redirect, url_for, session
from router import router

@router.route('/view_text')
def view_text():
    pdf_name = session.get('pdf_name', None)
    pdf_text = session.get('pdf_text', '')
    if not pdf_name:
        flash('No PDF has been uploaded yet. Please upload a PDF first.')
        return redirect(url_for('router.upload_file'))
    if not pdf_text:
        flash('No text content found. Please upload a PDF first.')
        return redirect(url_for('router.upload_file'))
    return render_template('view_text.html', pdf_name=pdf_name, pdf_text=pdf_text)
