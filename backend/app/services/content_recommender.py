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
        
        from app.services.model_manager import model_manager

        for weakness in top_weaknesses:
            topic = weakness['topic']
            subject = weakness['subject']
            
            # 2. AI-Driven Smart Search Intent
            if model_manager.is_configured:
                try:
                    search_prompt = f"""
                    # MISSION: GENERATE SMART SEARCH QUERY
                    **Topic:** {topic} ({subject})
                    **Context:** User is weak in this area. Needs high-yield UPSC content.

                    **OUTPUT:**
                    Return specific YouTube search terms.
                    Example: "Mrunal Patel Economy Inflation Playlist" or "Sleepy Classes Art and Culture Temple Architecture".
                    Just the query text.
                    """
                    response = model_manager.generate_content(search_prompt, model_type='fast')
                    smart_query = response.text.strip()

                    recommendations.append({
                        'type': 'youtube_search_intent',
                        'topic': topic,
                        'title': f"Watch: {smart_query}",
                        'link': f"https://www.youtube.com/results?search_query={smart_query.replace(' ', '+')}",
                        'reason': f"AI suggested high-yield video search for {topic}"
                    })
                except:
                    pass

            # 3. Fallback to Ravens (News)
            articles = RavensService.search_articles(topic)
            if articles:
                article = articles[0]
                recommendations.append({
                    'type': 'article',
                    'topic': topic,
                    'title': article['title'],
                    'link': article['link'],
                    'reason': f"Recent news linkage for {topic}"
                })
                
            if len(recommendations) >= limit:
                break
                    
        return recommendations
