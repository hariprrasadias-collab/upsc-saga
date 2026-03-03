from flask import Blueprint, jsonify
from app.db import get_db
import time

health_bp = Blueprint('health', __name__)

START_TIME = time.time()

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check returning OK and DB status."""
    status = "ok"
    db_status = "ok"
    try:
        conn = get_db()
        conn.execute('SELECT 1').fetchone()
    except Exception as e:
        db_status = f"error: {str(e)}"
        status = "error"

    response = {
        "status": status,
        "db": db_status,
        "timestamp": time.time()
    }
    
    # Bypass standard envelope by using a direct tuple return for error states if needed,
    # but the envelope middleware will automatically wrap this nicely.
    # However, standard health checks often prefer raw JSON. Our middleware unwraps if `success` exists.
    # To bypass it cleanly, we can just return standard raw JSON and let wrapper handle it.
    
    code = 200 if status == "ok" else 503
    return jsonify(response), code


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """Aggregate application metrics for dashboards."""
    try:
        conn = get_db()
        
        # Simple stats
        total_questions = conn.execute('SELECT COUNT(*) FROM pyq_questions').fetchone()[0]
        try:
            total_flashcards = conn.execute('SELECT COUNT(*) FROM flashcards').fetchone()[0]
        except Exception:
            total_flashcards = 0
            
        try:
            total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        except Exception:
            total_users = 0

        uptime = time.time() - START_TIME

        metrics_data = {
            "uptime_seconds": round(uptime, 2),
            "total_questions": total_questions,
            "total_flashcards": total_flashcards,
            "total_users": total_users,
        }

        return jsonify(metrics_data)
    except Exception as e:
        return jsonify({"error": f"Failed to gather metrics: {str(e)}"}), 500
