from flask import Flask, render_template, request, jsonify, session
from flask import Response,  stream_with_context

import importlib.util
import inspect
import uuid

import os
import time
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session management

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

# Initialize agent manager
agent_manager = AgentManager()

@app.route('/')
def index():
    """Main page"""
    agents = agent_manager.get_available_agents()
    return render_template('index.html', agents=agents)

@app.route('/summarize', methods=['POST'])
def summarize():
    """Handle summarization request"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        agent_name = data.get('agent', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not agent_name:
            return jsonify({'error': 'No agent selected'}), 400
        
        # Get agent instance
        agent = agent_manager.get_agent_instance(agent_name)
        if not agent:
            return jsonify({'error': f'Agent {agent_name} not found'}), 404
        
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())
        
        # Perform summarization
        summary = agent.summarize_text(text)
        
        # Store in session for history
        if 'history' not in session:
            session['history'] = []
        
        session['history'].append({
            'id': request_id,
            'agent': agent_name,
            'original_text': text[:200] + '...' if len(text) > 200 else text,
            'summary': summary,
            'timestamp': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Keep only last 10 entries
        session['history'] = session['history'][-10:]
        session.modified = True
        
        return jsonify({
            'success': True,
            'summary': summary,
            'agent': agent_name,
            'request_id': request_id,
            'text_length': len(text)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# @app.route('/summarize_stream', methods=['POST'])
# def summarize_stream():
#     """Handle summarization request with streaming response"""
#     try:
#         data = request.get_json()
#         text = data.get('text', '').strip()
#         agent_name = data.get('agent', '')

#         if not text:
#             return jsonify({'error': 'No text provided'}), 400

#         if not agent_name:
#             return jsonify({'error': 'No agent selected'}), 400

#         # Get agent instance
#         agent = agent_manager.get_agent_instance(agent_name)
#         if not agent:
#             return jsonify({'error': f'Agent {agent_name} not found'}), 404

#         # Generate unique ID for this request
#         request_id = str(uuid.uuid4())

#         def generate():
#             summary_chunks = agent.summarize_text(text) 
#             for chunk in summary_chunks:
#                 yield f"data: {chunk}\n\n"

#         response_headers = {
#             'Content-Type': 'text/event-stream',
#             'Cache-Control': 'no-cache',
#             'Transfer-Encoding': 'chunked'
#         }

#         return Response(stream_with_context(generate()), headers=response_headers)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

    
# @app.route('/summarize_stream', methods=['POST'])
# def summarize_stream():
#     data = request.get_json()
#     text = data.get('text', '')
#     agent = data.get('agent', 'DefaultAgent')

#     @stream_with_context
#     def generate():
#         yield json.dumps({'event': 'status', 'data': 'Initializing summarization'}) + '\n'
#         time.sleep(0.5)

#         words = text.strip().split()
#         chunk = ''
#         count = 0

#         for word in words:
#             chunk += word + ' '
#             count += 1

#             if count % 10 == 0:
#                 # simulate partial content streaming
#                 yield json.dumps({'event': 'content', 'data': chunk.strip()}) + '\n'
#                 chunk = ''
#                 time.sleep(0.2)  # simulate delay

#                 # send progress
#                 progress = min(int((count / len(words)) * 100), 100)
#                 yield json.dumps({'event': 'progress', 'progress': progress}) + '\n'

#         if chunk:
#             yield json.dumps({'event': 'content', 'data': chunk.strip()}) + '\n'

#         time.sleep(0.3)
#         yield json.dumps({
#             'event': 'complete',
#             'summary': ' '.join(words[:min(len(words), 100)]),
#             'agent': agent
#         }) + '\n'

#     return Response(generate(), mimetype='text/plain')    


@app.route('/history')
def history():
    """Get summarization history"""
    return jsonify(session.get('history', []))

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear summarization history"""
    session.pop('history', None)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
