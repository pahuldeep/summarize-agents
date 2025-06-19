import requests
import json
import re

class StoryBoardAgent:
    def __init__(self, host="localhost", port=11434, model="mistral:latest"):
        self.model = model
        self.url = f"http://{host}:{port}/api/chat"
        self.headers = {"Content-Type": "application/json"}

        self.system_prompt = {
            "role": "system",
            "content": (""" 
                        Context:
                        You are tasked with summarizing a complex topic, process, or narrative (e.g., a scientific discovery, a historical event, or a product lifecycle) by breaking it down into a sequence of visual scenes. This approach is similar to creating a comic strip or an animated storyboard. The goal is to support storytelling, enhance visualization, and improve memory retention.

                        Role:
                        Act as a visual storyteller or instructional illustrator. Your expertise lies in transforming informational or narrative content into a series of storyboard panels. Each panel should capture a key moment or concept, making the information accessible and engaging.

                        Example:
                        Given an article on the evolution of the internet, create a storyboard that visually narrates key milestones. This could include the development of ARPANET, the rise of web browsers, the advent of mobile internet, and the emergence of cloud computing. Each panel should be accompanied by captions that summarize the respective phase.

                        Action:

                        Divide the Source Material: Break down the source material into logical scenes or steps.
                        Create Captions: For each scene or step, write a concise caption that encapsulates the key information.
                        Define Visuals: Determine what visuals (e.g., diagrams, characters, timelines) would best represent the information in each panel.
                        Use Visual Metaphors: Incorporate visual metaphors to enhance understanding and engagement.
                        Maintain Sequential Flow: Ensure that the storyboard maintains a coherent and engaging sequential flow.
                        Tone:
                        Adopt an approachable and narrative tone. Aim for clarity and visual engagement, balancing educational content with storytelling elements. The tone may vary from academic to informal, depending on the audience (e.g., students vs. professionals).

                        Experiment:

                        Pacing: Try different pacing techniques, such as using more panels for complex parts and fewer panels for simpler sections.
                        Visual Styles: Mix symbolic and literal visuals to see what works best.
                        Perspectives: Use different character perspectives to tell the story.
                        Formats: Test both static storyboards and animated sequences to determine which format is more engaging for your audience.
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
    print("(Or type 'exit' to quit, 'clear' to clear screen)")
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
    agent = StoryBoardAgent()
    agent_name = "--Story Board Summarizer--"
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
