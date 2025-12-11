from app.services.model_manager import model_manager
import os

class AIModelWrapper:
    def __init__(self, strategy):
        self.strategy = strategy

    def generate_content(self, prompt):
        model_type = 'fast'
        if self.strategy == 'quality' or self.strategy == 'code':
            model_type = 'pro'
            
        return model_manager.generate_content(prompt, model_type=model_type)

class AIModelFactory:
    _configured = False

    @staticmethod
    def configure():
        # Configuration is now handled centrally by ModelManager
        pass

    @staticmethod
    def get_model(strategy='speed'):
        """
        Returns a model wrapper based on the requested strategy.
        Deprecated: Use model_manager directly where possible.
        """
        return AIModelWrapper(strategy)
