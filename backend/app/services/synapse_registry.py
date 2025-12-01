from typing import Dict, Any, Callable, List, Optional

class SynapseRegistry:
    """
    Registry for all 'Synapses' - connections to different features of the app.
    Allows the Brain to dynamically access data and trigger actions across the entire system.
    """
    _instance = None
    
    def __init__(self):
        self.synapses: Dict[str, Dict[str, Any]] = {
            'CORE': {},
            'KNOWLEDGE': {},
            'ASSESSMENT': {},
            'ENGAGEMENT': {},
            'AI_TOOLS': {}
        }
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SynapseRegistry()
        return cls._instance

    def register_synapse(self, category: str, name: str, service_ref: Any, description: str):
        """
        Register a feature service as a synapse.
        
        Args:
            category: One of 'CORE', 'KNOWLEDGE', 'ASSESSMENT', 'ENGAGEMENT', 'AI_TOOLS'
            name: Unique name (e.g., 'pomodoro', 'ravens')
            service_ref: Reference to the service module or class instance
            description: Description of what this synapse provides to the Brain
        """
        if category not in self.synapses:
            print(f"Warning: Unknown synapse category '{category}'. Defaulting to 'CORE'.")
            category = 'CORE'
            
        self.synapses[category][name] = {
            'ref': service_ref,
            'description': description,
            'status': 'active'
        }
        print(f"🧠 Synapse Connected: [{category}] {name}")

    def get_synapse(self, name: str) -> Optional[Any]:
        """Retrieve a specific synapse by name."""
        for category in self.synapses:
            if name in self.synapses[category]:
                return self.synapses[category][name]['ref']
        return None

    def get_all_synapses(self) -> Dict[str, Dict[str, Any]]:
        """Get the full map of the nervous system."""
        return self.synapses

    def scan_category(self, category: str) -> List[str]:
        """List all active synapses in a category."""
        return list(self.synapses.get(category, {}).keys())
