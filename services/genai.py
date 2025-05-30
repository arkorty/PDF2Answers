import os
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your_gemini_api_key")
genai.configure(api_key=GEMINI_API_KEY)

def generate_answer(pdf_text, question):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    Based on the following document, please answer the question.
    Document content: {pdf_text}
    
    Question: {question}

    Note: Respond in plaintext, not markdown.
    """
    response = model.generate_content(prompt)
    return response.text
