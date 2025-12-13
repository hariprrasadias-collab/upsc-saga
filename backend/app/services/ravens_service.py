from app.db_models.current_affairs import get_saved_articles
import traceback

class RavensService:
    """
    Service for accessing News/Current Affairs (Ravens).
    """
    @staticmethod
    def get_recent_articles(limit=5):
        """Get most recent articles for the Brain context."""
        try:
            articles = get_saved_articles()
            if not articles:
                return []
            return articles[:limit]
        except Exception as e:
            print(f"Ravens Fetch Error: {e}")
            return []

    @staticmethod
    def search_articles(query):
        """Search articles by keyword."""
        try:
            return get_saved_articles({'search': query})
        except Exception:
            return []

    @staticmethod
    def get_article_by_link(link):
        """Check if article exists and return it."""
        try:
            all_articles = get_saved_articles()
            for a in all_articles:
                if a['link'] == link:
                    return a
            return None
        except Exception:
            return None

    @staticmethod
    def get_brain_context():
        """Standard interface for the Brain to pull context."""
        try:
            recent = RavensService.get_recent_articles(limit=3)
            return {
                "status": "active",
                "data": {
                    "recent_headlines": [a['title'] for a in recent] if recent else []
                }
            }
        except Exception as e:
            return {"status": "error", "data": {"recent_headlines": []}}

    @staticmethod
    def generate_upsc_summary(article_content):
        """
        Uses AI to convert raw news into a high-yield UPSC summary.
        """
        from app.services.model_manager import model_manager

        prompt = f"""
        # MISSION: CURRENT AFFAIRS FILTER (THE HINDU/IE)
        **Input:**
        "{article_content[:15000]}..."

        **DIRECTIVE:**
        You are the UNIVERSAL WEAVER. Transmute this text into an Omega Tier study module.

        **ARCHITECTURAL DIRECTIVES:**
        1. **Deep Analysis:** STEEPLE Framework.
        2. **Facts:** Prelims Armory (Data/Reports).
        3. **Visuals:** Mermaid.js Mindmap & Data Viz (Chart).
        4. **Audio:** Podcast Script (Host/Expert).
        5. **Simulation:** Interview Questions & Ethics Scenario.
        6. **Chronology:** Timeline of events.

        **OUTPUT SCHEMA (JSON):**
        {{
            "headline": "Punchy Title",
            "gs_mapping": ["GS2 (Polity)", "GS3 (Economy)"],
            "prelims_facts": ["Fact 1", "Fact 2"],
            "mains_arguments": {{ "pros": ["..."], "cons": ["..."], "way_forward": ["..."] }},
            "keywords": ["K1", "K2"],
            "summary": "Deep summary (200 words)...",
            "steeple_analysis": {{ "social": "...", "economic": "..." }},
            "inter_linkages": ["GS2: ...", "GS3: ..."],
            "mind_map": "graph TD; ...",
            "quiz": [ {{ "question": "...", "options": [], "answer": "...", "explanation": "..." }} ],
            "answer_framework": {{ "intro": "...", "body_points": [], "conclusion": "..." }},
            "essay_fodder": {{ "quote": "...", "statistic": "..." }},
            "timeline": [ {{ "date": "...", "event": "..." }} ],
            "data_visualization": {{ "type": "bar", "data": [] }},
            "podcast_script": "Host: ... Expert: ...",
            "interview_questions": [ {{ "question": "...", "context": "..." }} ],
            "simulation_scenario": {{ "scenario": "...", "options": [] }}
        }}
        """
        try:
            response = model_manager.generate_content(prompt, model_type='pro')
            return response.text
        except Exception:
            return "{}"

# Register Synapse
try:
    from app.services.synapse_registry import SynapseRegistry
    SynapseRegistry.get_instance().register_synapse(
        category='KNOWLEDGE',
        name='ravens',
        service_ref=RavensService,
        description='Access to Current Affairs, News, and UPSC Summaries.'
    )
except ImportError:
    pass
