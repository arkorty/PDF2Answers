from flask import render_template
from router import router

@router.route("/")
def home():
    return render_template('home.html')
