from flask import jsonify
from router import router

@router.route("/api/status")
def api_status():
    status = {
        "status": "true",
        "message": "Server is running",
        "version": "1.0.0"
    }
    return jsonify(status)
