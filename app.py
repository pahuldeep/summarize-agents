from agent_manage import AgentManager
import uuid
import os

from flask import Flask, render_template, request, jsonify, session, Response

import json
import re 

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session management


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
    
@app.route('/summarize_stream', methods=['POST'])
def summarize_stream():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        agent_name = data.get('agent', '')

        if not text:
            return jsonify({'error': 'No text provided'}), 400
        if not agent_name:
            return jsonify({'error': 'No agent selected'}), 400

        agent = agent_manager.get_agent_instance(agent_name)
        if not agent:
            return jsonify({'error': f'Agent {agent_name} not found'}), 404

        agent.prepare_messages(text)
        payload = agent.build_payload()
        response = agent.send_streaming_request(payload)

        # def token_stream():
        #     if not response:
        #         yield 'data: [ERROR] Could not connect\n\n'
        #         return

        #     for line in response.iter_lines():
        #         if line:
        #             try:
        #                 res = json.loads(line.decode('utf-8'))
        #                 chunk = res.get('message', {}).get('content', '')
        #                 if chunk.strip():
        #                     # Escape newlines for SSE
        #                     yield f'{chunk}'
        #             except Exception as e:
        #                 yield f'data: [ERROR] {str(e)}\n\n'

        def paragraph_stream():
            if not response:
                yield '[ERROR] Could not connect'
                return

            buffer = ""
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    res = json.loads(line.decode('utf-8'))
                    chunk = res.get('message', {}).get('content', '')
                    if not chunk:
                        continue

                    buffer += chunk

                    # Emit paragraph if newlines or sentence boundary detected
                    while True:
                        # Find paragraph or sentence delimiter
                        match = re.search(r'(.+?)([\n]{2,}|[.!?])(\s|$)', buffer)
                        if not match:
                            break
                        segment = match.group(1) + match.group(2)
                        yield segment.strip()
                        buffer = buffer[match.end():]

                except Exception as e:
                    yield f"[ERROR] Streaming error: {str(e)}"

            if buffer.strip():
                yield buffer.strip()  # Emit remainder

        return Response(paragraph_stream(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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