import requests
import json
import re

class ContextMapperAgent:
    def __init__(self, host="localhost", port=11434, model="gemma3:latest"):
        self.model = model
        self.url = f"http://{host}:{port}/api/chat"
        self.headers = {"Content-Type": "application/json"}

        self.system_prompt = {
            "role": "system",
            "content": (""" 
                        Context: You are working with a dense, information-rich source (such as a textbook chapter, research paper, or technical manual) and need to visually organize its contents to clarify relationships between key ideas, categories, processes, and hierarchies.

                        Role: Act as a knowledge architect or instructional designer skilled in transforming complex textual data into intuitive concept maps or network diagrams for enhanced learning and memory retention.

                        Example: Given a chapter on neural networks, create a concept map that visually links core components such as input layers, activation functions, backpropagation, loss functions, and optimization algorithms, showing how they interconnect in the learning process.

                        Action: Extract major concepts, identify their relationships (e.g., cause-effect, parent-child, process steps), and organize them into a visual structure such as a flowchart, spider diagram, or hierarchical map. Highlight cross-links where applicable to show deeper associations.

                        Tone: Use a clear, instructional tone with succinct labels and logical flow. Prioritize clarity over aesthetics to support comprehension for learners or analysts.

                        Experiment: Explore different mapping styles (e.g., radial vs. linear vs. layered) or tools (e.g., Mermaid.js, draw.io, Excalidraw). Test alternative groupings, abstractions, or metaphors to present complex relationships more intuitively.
                        """
                    )
                }


    def prepare_messages(self, user_content):
        # Normalize text: remove excessive whitespace and line breaks
        cleaned_text = re.sub(r'\s+', ' ', user_content.strip())
        self.messages = [
            self.system_prompt,
            {"role": "user", "content": cleaned_text}
        ]


    def build_payload(self):
        return {
            "model": self.model,
            "options": {"temperature": 0.0},
            "stream": True,
            "messages": self.messages
        }


    def send_streaming_request(self, payload):
        try:
            response = requests.post(self.url, json=payload, headers=self.headers, stream=True)
            if response.status_code == 200:
                return response
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def process_stream(self, response, display_output=True):
        full_reply = ""
        if display_output:
            print("\nSUMMARIZED-AI: ", end='', flush=True)
        try:
            for line in response.iter_lines():
                if line:
                    try:
                        res = json.loads(line.decode('utf-8'))
                        content = res.get('message', {}).get('content', '')
                        if display_output:
                            print(content, end='', flush=True)
                        full_reply += content
                    except json.JSONDecodeError as e:
                        print(f"\n[Error decoding JSON in stream: {e}]")
                        continue
                    except Exception as e:
                        print(f"\n[Error processing stream chunk: {e}]")
                        continue
            if display_output:
                print()  # newline after summary
            return full_reply
        finally:
            response.close()

    def summarize_text(self, text: str) -> str:
        """Main method to summarize text with error handling"""
        if not text.strip():
            return "No text provided to summarize."
        
        try:
            self.prepare_messages(text)
            payload = self.build_payload()
            response = self.send_streaming_request(payload)
            
            if response:
                return self.process_stream(response)
            else:
                return "Failed to get response from the API."
                
        except Exception as e:
            return f"Error during summarization: {e}"




def get_multiline_input(agent_name):
    """Get multi-line input from user, handling paste operations properly"""
    print(f"Enter text to: {agent_name} (paste your text and press Enter twice to finish):")
    print("(Type 'exit' to quit, 'clear' to clear screen)")
    print("> ", end='', flush=True)
    
    lines = []
    empty_line_count = 0
    
    try:
        while True:
            try:
                line = input()
                
                # Check for commands
                if line.strip().lower() in {"exit", "quit"}:
                    return "EXIT"
                elif line.strip().lower() == "clear":
                    return "CLEAR"
                
                # If line is empty, increment counter
                if not line.strip():
                    empty_line_count += 1
                    # If we get two empty lines in a row, finish input
                    if empty_line_count >= 2:
                        break
                else:
                    empty_line_count = 0
                    lines.append(line)
                    
            except EOFError:
                # Handle Ctrl+D
                return "EXIT"
                
                
    except KeyboardInterrupt:
        return "INTERRUPT"
    
    # Join all lines and return
    full_text = '\n'.join(lines).strip()
    return full_text if full_text else None

def run_chat():
    agent = ContextMapperAgent()
    agent_name = "--ContextMapper Summarizer"
    print(agent_name)
    print("Tip: You can paste multi-line text directly. Press Enter twice when done.")
    
    while True:
        try:
            print("\n" + "="*60)
            
            # Get multi-line input
            user_input = get_multiline_input(agent_name)
            
            if user_input == "EXIT":
                print("Exiting. Goodbye!") 
                break
            
            elif user_input == "CLEAR":
                print("\033[2J\033[H")  # Clear screen
                print(agent_name)
                print("Tip: You can paste multi-line text directly. Press Enter twice when done.")
                continue
            
            elif user_input == "INTERRUPT":
                print("\nUse 'exit' to quit properly.")
                continue
            elif not user_input:
                print("No text entered. Please provide some text to summarize.")
                continue

            # Show what we received (truncated)
            print(f"\nReceived text ({len(user_input)} characters)")
            agent.summarize_text(user_input)
            
                
        except KeyboardInterrupt:
            print("\n\nUse 'exit' to quit properly.")
            continue
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            continue

if __name__ == "__main__":
    run_chat()

