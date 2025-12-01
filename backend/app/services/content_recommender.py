from app.services.weak_area_service import WeakAreaAnalyzer
from app.services.ravens_service import RavensService
from app.db import get_db
import json

class ContentRecommender:
    """
    Service to recommend content (articles, notes) based on user context.
    """
    
    @staticmethod
    def get_recommendations_for_weak_areas(user_id=1, limit=3):
        """
        Get content recommendations for the user's top weak areas.
        """
        recommendations = []
        
        # 1. Get Weak Areas
        weak_areas = WeakAreaAnalyzer.analyze_user_performance(user_id)
        if not weak_areas:
            return []
            
        # Take top 3 weak areas
        top_weaknesses = weak_areas[:3]
        
        for weakness in top_weaknesses:
            topic = weakness['topic']
            subject = weakness['subject']
            
            # 2. Search Ravens for this topic
            # We search for the topic name
            articles = RavensService.search_articles(topic)
            
            if articles:
                # Pick the most relevant/recent one (first one)
                article = articles[0]
                
                recommendations.append({
                    'type': 'article',
                    'topic': topic,
                    'title': article['title'],
                    'link': article['link'],
                    'reason': f"Recommended to improve your score in {topic} ({subject})"
                })
                
                if len(recommendations) >= limit:
                    break
                    
        return recommendations
