import json
from app.db import get_db
from datetime import datetime
from email.utils import parsedate_to_datetime

class CompilationService:
    @staticmethod
    def parse_date(date_str):
        """
        Parse date string trying multiple formats (ISO, RSS/RFC 2822).
        Returns a datetime object or None.
        """
        if not date_str:
            return None
            
        # Try ISO format first (YYYY-MM-DD...)
        try:
            # Handle simple YYYY-MM-DD
            if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
                return datetime.strptime(date_str, "%Y-%m-%d")
            return datetime.fromisoformat(date_str)
        except ValueError:
            pass
            
        # Try RSS format (RFC 2822) e.g., "Sun, 23 Nov 2025 10:02:01 +0530"
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            pass
            
        return None

    @staticmethod
    def get_monthly_compilation(year, month):
        """
        Fetch articles for a specific month and year, grouped by subject.
        Enhanced with full data, importance sorting, and better organization.
        """
        conn = get_db()
        
        # Fetch ALL articles and filter in Python due to inconsistent date formats
        query = 'SELECT * FROM current_affairs ORDER BY subjects, importance DESC, published_date DESC'
        rows = conn.execute(query).fetchall()
        
        compilation = {
            "year": year,
            "month": month,
            "generated_at": datetime.now().isoformat(),
            "total_articles": 0,
            "subjects": {},
            "stats": {
                "high_importance": 0,
                "medium_importance": 0,
                "low_importance": 0
            }
        }
        
        for row in rows:
            pub_date_str = row['published_date']
            fetch_date_str = row['fetch_date']
            
            # Use published_date, fallback to fetch_date
            dt = CompilationService.parse_date(pub_date_str)
            if not dt:
                dt = CompilationService.parse_date(fetch_date_str)
                
            if not dt:
                continue
                
            # Filter by year and month
            if dt.year == year and dt.month == month:
                article = {
                    'id': row['id'],
                    'title': row['title'],
                    'upsc_summary': row['upsc_summary'] or '',  # FULL summary, no truncation
                    'original_summary': row['original_summary'] or '',
                    'key_points': json.loads(row['key_points'] or '[]'),
                    'papers': json.loads(row['papers'] or '[]'),
                    'subjects': json.loads(row['subjects'] or '[]'),
                    'published_date': pub_date_str or fetch_date_str,
                    'source': row['source'],
                    'importance': row['importance'],
                    'link': row['original_link'],
                    'image_url': row['image_url'] or '',
                    'related_pyqs': json.loads(row['related_pyqs'] or '[]')
                }
                
                # Track importance stats
                if article['importance'] == 3:
                    compilation['stats']['high_importance'] += 1
                elif article['importance'] == 2:
                    compilation['stats']['medium_importance'] += 1
                else:
                    compilation['stats']['low_importance'] += 1
                
                # Group by primary subject
                subjects_list = article['subjects']
                primary_subject = subjects_list[0] if subjects_list else "Miscellaneous"
                
                if primary_subject not in compilation["subjects"]:
                    compilation["subjects"][primary_subject] = []
                    
                compilation["subjects"][primary_subject].append(article)
                compilation["total_articles"] += 1
        
        # Sort articles within each subject by importance (High → Medium → Low)
        for subject in compilation["subjects"]:
            compilation["subjects"][subject].sort(
                key=lambda x: (-x['importance'], x['published_date']), 
                reverse=False
            )
            
        return compilation

    @staticmethod
    def get_available_months():
        """
        Get a list of months that have articles.
        Always includes current month at the top.
        """
        conn = get_db()
        rows = conn.execute("SELECT published_date, fetch_date FROM current_affairs").fetchall()
        
        months_set = set()
        
        # Always add current month
        now = datetime.now()
        months_set.add((now.year, now.month))
        
        for row in rows:
            dt = CompilationService.parse_date(row['published_date'])
            if not dt:
                dt = CompilationService.parse_date(row['fetch_date'])
            
            if dt:
                months_set.add((dt.year, dt.month))
                
        # Sort descending
        sorted_months = sorted(list(months_set), key=lambda x: (x[0], x[1]), reverse=True)
        
        months = []
        for y, m in sorted_months:
            label = datetime(y, m, 1).strftime("%B %Y")
            # Mark current month
            is_current = (y == now.year and m == now.month)
            if is_current:
                label = f"{label} (Current)"
            
            months.append({
                "year": y,
                "month": m,
                "label": label,
                "is_current": is_current
            })
            
        return months

