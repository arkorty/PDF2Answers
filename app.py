from flask import Flask, render_template
from router import router
import os
from flask_session import Session
from dotenv import load_dotenv
import sys

load_dotenv('.flaskenv')

REQUIRED_KEYS = ['GEMINI_API_KEY']
missing_keys = [key for key in REQUIRED_KEYS if not os.getenv(key)]
if missing_keys:
    print(f"Error: Missing required API keys: {', '.join(missing_keys)}")
    sys.exit(1)

app = Flask(__name__)
app.register_blueprint(router, url_prefix="/")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.secret_key = 'development_key_12345'

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
