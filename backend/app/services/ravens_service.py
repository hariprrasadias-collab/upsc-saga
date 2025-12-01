from app.db_models.current_affairs import get_saved_articles, article_exists

class RavensService:
    """
    Service for accessing News/Current Affairs (Ravens).
    """
    @staticmethod
    def get_recent_articles(limit=5):
        """Get most recent articles for the Brain context."""
        articles = get_saved_articles()
        return articles[:limit]

    @staticmethod
    def search_articles(query):
        """Search articles by keyword."""
        return get_saved_articles({'search': query})

    @staticmethod
    def get_article_by_link(link):
        """Check if article exists and return it."""
        # This is a simplified check, ideally we'd get the full object
        # For now, we reuse the existing list fetch
        all_articles = get_saved_articles()
        for a in all_articles:
            if a['link'] == link:
                return a
        return None

    @staticmethod
    def get_brain_context():
        """Standard interface for the Brain to pull context."""
        recent = RavensService.get_recent_articles(limit=3)
        return {
            "status": "active",
            "data": {
                "recent_headlines": [a['title'] for a in recent] if recent else []
            }
        }

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
