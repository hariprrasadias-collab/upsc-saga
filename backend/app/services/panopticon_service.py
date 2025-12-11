import sqlite3
import json
import math
from datetime import datetime, timedelta
from flask import current_app
import os

# Configure Gemini
from app.services.model_manager import model_manager

# Configure Gemini (Removed local config)
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel('gemini-pro')

class PanopticonService:
    def __init__(self):
        pass

    # ... (rest of methods until _generate_insight)

    def _generate_insight(self, metric, perf, r):
        """Use Gemini to generate a human-readable insight."""
        prompt = f"""
        Analyze this correlation data for a student:
        Metric: {metric}
        Performance: {perf}
        Correlation Coefficient (r): {r:.2f}
        
        Explain what this means for their study routine in 1 short sentence.
        If r > 0.5: Strong positive (Doing X helps Y).
        If r < -0.5: Strong negative (Doing X hurts Y).
        If r is near 0: No relation.
        """
        try:
            # Use ModelManager for rate limiting and load balancing
            response = model_manager.generate_content(prompt, model_type='fast')
            return response.text.strip()
        except:
            return f"Correlation between {metric} and {perf} is {r:.2f}."
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn

    def log_daily_metrics(self, data):
        """
        Log daily bio-metrics.
        data: {date, sleep_hours, sleep_quality, mood_score, energy_level, diet_quality, exercise_minutes, notes}
        """
        conn = self.get_db_connection()
        if not conn: return {"success": False, "message": "Database Unavailable"}

        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO daily_biometrics (date, sleep_hours, sleep_quality, mood_score, energy_level, diet_quality, exercise_minutes, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    sleep_hours=excluded.sleep_hours,
                    sleep_quality=excluded.sleep_quality,
                    mood_score=excluded.mood_score,
                    energy_level=excluded.energy_level,
                    diet_quality=excluded.diet_quality,
                    exercise_minutes=excluded.exercise_minutes,
                    notes=excluded.notes
            ''', (
                data['date'], data.get('sleep_hours'), data.get('sleep_quality'), 
                data.get('mood_score'), data.get('energy_level'), data.get('diet_quality'), 
                data.get('exercise_minutes'), data.get('notes')
            ))
            conn.commit()
            
            # Trigger analysis after logging
            self.analyze_correlations()
            
            return {"success": True, "message": "Bio-metrics logged successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            conn.close()

    def _calculate_pearson_correlation(self, x, y):
        """Calculate Pearson correlation coefficient between two lists."""
        n = len(x)
        if n != len(y) or n < 2:
            return 0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x_sq = sum(xi*xi for xi in x)
        sum_y_sq = sum(yi*yi for yi in y)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x_sq - sum_x**2) * (n * sum_y_sq - sum_y**2))
        
        if denominator == 0:
            return 0
            
        return numerator / denominator

    def get_current_status(self):
        """
        Get the latest bio-status from the database.
        Returns a dict with status, energy, and any alerts.
        """
        conn = self.get_db_connection()
        if not conn: return {"status": "UNKNOWN", "energy": 50, "alert": "DB Error"}

        cursor = conn.cursor()
        
        try:
            # Fetch latest entry
            cursor.execute('''
                SELECT * FROM daily_biometrics 
                ORDER BY date DESC LIMIT 1
            ''')
            row = cursor.fetchone()
            
            if not row:
                return {"status": "UNKNOWN", "energy": 50, "alert": "No Data"}
                
            data = dict(row)
            energy = data.get('energy_level', 50)
            sleep = data.get('sleep_hours', 7)
            
            # Determine Status
            status = "OPTIMAL"
            alert = None
            
            if energy < 40 or sleep < 5:
                status = "CRITICAL"
                alert = "High Fatigue Detected"
            elif energy < 70 or sleep < 6.5:
                status = "FATIGUED"
                alert = "Recovery Recommended"
                
            return {
                "status": status,
                "energy": energy,
                "alert": alert,
                "last_updated": data.get('date')
            }
            
        except Exception as e:
            print(f"Panopticon Status Check Failed: {e}")
            return {"status": "ERROR", "energy": 0, "alert": str(e)}
        finally:
            conn.close()

    def analyze_correlations(self):
        """
        Analyze correlations between bio-metrics and study performance.
        """
        conn = self.get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        
        try:
            # 1. Fetch Bio-Metrics (Last 30 days)
            cursor.execute('''
                SELECT date, sleep_hours, mood_score, energy_level
                FROM daily_biometrics
                ORDER BY date DESC LIMIT 30
            ''')
            biometrics = {row['date']: dict(row) for row in cursor.fetchall()}
            
            # 2. Fetch Study Performance (Quiz Scores)
            # Check if table exists first to avoid crash
            try:
                cursor.execute("SELECT 1 FROM pyq_quiz_sessions LIMIT 1")
            except sqlite3.OperationalError:
                conn.close()
                return

            cursor.execute('''
                SELECT date(submitted_at) as date, AVG(score) as avg_score
                FROM pyq_quiz_sessions
                WHERE status = 'completed' AND submitted_at IS NOT NULL
                GROUP BY date(submitted_at)
                ORDER BY date DESC LIMIT 30
            ''')
            scores = {row['date']: row['avg_score'] for row in cursor.fetchall()}
            
            # 3. Align Data
            dates = sorted(list(set(biometrics.keys()) & set(scores.keys())))
            if len(dates) < 3:
                conn.close()
                return # Not enough data

            sleep_data = [biometrics[d]['sleep_hours'] for d in dates if biometrics[d]['sleep_hours'] is not None]
            mood_data = [biometrics[d]['mood_score'] for d in dates if biometrics[d]['mood_score'] is not None]
            score_data_sleep = [scores[d] for d in dates if biometrics[d]['sleep_hours'] is not None]
            score_data_mood = [scores[d] for d in dates if biometrics[d]['mood_score'] is not None]
            
            # 4. Calculate Correlations
            correlations = []
            
            if len(sleep_data) > 2:
                r_sleep = self._calculate_pearson_correlation(sleep_data, score_data_sleep)
                correlations.append(('sleep_hours', 'quiz_score', r_sleep))

            if len(mood_data) > 2:
                r_mood = self._calculate_pearson_correlation(mood_data, score_data_mood)
                correlations.append(('mood_score', 'quiz_score', r_mood))

            # 5. Generate Insights & Save
            for metric, perf, r in correlations:
                insight = self._generate_insight(metric, perf, r)

                cursor.execute('''
                    INSERT INTO bio_correlations (metric_name, performance_metric, correlation_coefficient, insight_text)
                    VALUES (?, ?, ?, ?)
                ''', (metric, perf, r, insight))

            conn.commit()
        except Exception as e:
            print(f"Panopticon Analysis Failed: {e}")
        finally:
            conn.close()

    def _generate_insight(self, metric, perf, r):
        """Use Gemini to generate a human-readable insight."""
        prompt = f"""
        Analyze this correlation data for a student:
        Metric: {metric}
        Performance: {perf}
        Correlation Coefficient (r): {r:.2f}
        
        Explain what this means for their study routine in 1 short sentence.
        If r > 0.5: Strong positive (Doing X helps Y).
        If r < -0.5: Strong negative (Doing X hurts Y).
        If r is near 0: No relation.
        """
        try:
            # Use ModelManager for robustness
            response = model_manager.generate_content(prompt, model_type='fast')
            return response.text.strip()
        except:
            return f"Correlation between {metric} and {perf} is {r:.2f}."

    def get_dashboard_data(self):
        """Get data for the frontend dashboard."""
        conn = self.get_db_connection()
        if not conn: return {"recent_metrics": [], "correlations": []}
        cursor = conn.cursor()
        
        try:
            # Get recent metrics
            cursor.execute('SELECT * FROM daily_biometrics ORDER BY date DESC LIMIT 7')
            recent_metrics = [dict(row) for row in cursor.fetchall()]

            # Get correlations
            cursor.execute('''
                SELECT * FROM bio_correlations
                WHERE id IN (SELECT MAX(id) FROM bio_correlations GROUP BY metric_name)
            ''')
            correlations = [dict(row) for row in cursor.fetchall()]

            return {
                "recent_metrics": recent_metrics,
                "correlations": correlations
            }
        except Exception:
            return {"recent_metrics": [], "correlations": []}
        finally:
            conn.close()

panopticon = PanopticonService()
