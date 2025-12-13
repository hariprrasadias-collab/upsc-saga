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
        You are a UPSC Chief Examiner. Analyze this text and provide a "Titan Level" summary.
        Extract ONLY what matters for UPSC. Disregard political gossip.

        **ANALYSIS FRAMEWORK (STEEPLE):**
        Analyze using Social, Technological, Economic, Environmental, Political, Legal, and Ethical dimensions where applicable.

        **OUTPUT SCHEMA (JSON):**
        {{
            "headline": "Punchy Title",
            "gs_mapping": ["GS2 (Polity)", "GS3 (Economy)"],
            "prelims_facts": ["Fact 1 (Data/Committee)", "Fact 2"],
            "mains_arguments": {{
                "pros": ["Arg 1"],
                "cons": ["Arg 2"],
                "way_forward": ["Committee Recommendation"]
            }},
            "keywords": ["Keyword1", "Keyword2"],
            "summary": "Comprehensive paragraph summary using STEEPLE framework implicitly",
            "steeple_analysis": {{
                "social": "Impact on society...",
                "economic": "Fiscal burden...",
                "legal": "Supreme Court judgement..."
            }},
            "inter_linkages": ["GS2: Federalism", "GS3: Fiscal Deficit"]
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
