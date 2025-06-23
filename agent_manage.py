import importlib.util
import inspect
import os

class AgentManager:
    def __init__(self):
        self.agents = {}
        self.agent_classes = {}
        self.load_agents()
    
    def load_agents(self):
        """Dynamically load agent classes from Python files"""
        # You can extend this to scan a directory for agent files
        agent_files = [
            'agents/condensed_agent.py',
            'agents/descriptive_agent.py',
            'agents/context_agent.py',
            'agents/storyboard_agent.py',
        ]
        
        for file_path in agent_files:
            if os.path.exists(file_path):
                try:
                    self.load_agent_from_file(file_path)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
    
    def load_agent_from_file(self, file_path):
        """Load agent class from a Python file"""
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find agent classes in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                name.endswith('Agent') and 
                hasattr(obj, 'summarize_text')):
                
                agent_display_name = self.format_agent_name(name)
                self.agent_classes[agent_display_name] = obj
                print(f"Loaded agent: {agent_display_name}")
    
    def format_agent_name(self, class_name):
        """Convert class name to display name"""
        # Convert CamelCase to Title Case
        import re
        name = re.sub(r'([A-Z])', r' \1', class_name).strip()
        return name.replace('Agent', '').strip()
    
    def get_agent_instance(self, agent_name):
        """Get or create agent instance"""
        if agent_name not in self.agents:
            if agent_name in self.agent_classes:
                try:
                    self.agents[agent_name] = self.agent_classes[agent_name]()
                except Exception as e:
                    print(f"Error creating {agent_name} instance: {e}")
                    return None
        return self.agents.get(agent_name)
    
    def get_available_agents(self):
        """Get list of available agent names"""
        return list(self.agent_classes.keys())