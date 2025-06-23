import requests
import json
import re

class StoryBoardAgent:
    def __init__(self, host="localhost", port=11434, model="llama3.2"):
        self.model = model
        self.url = f"http://{host}:{port}/api/chat"
        self.headers = {"Content-Type": "application/json"}

        # ++++++++++++++++++++++++++++++++++++
        # Prompts for the StoryBoardAgent
        # ++++++++++++++++++++++++++++++++++++

            # 1. Prompt: "Develop a comprehensive storyboard for a complex narrative, incorporating visual elements to 
            # boost comprehension and recall."

            # 2. Prompt: "Create a visually-driven sequence that outlines a detailed story, leveraging the power of 
            # sequential imagery to enhance memory retention."

            # 3. Prompt: "Design a series of illustrations that tell a story in a comic strip or animated format, 
            # utilizing visual narratives to improve understanding and recall."

            # 4. Prompt: "Generate a visual representation of a story in a sequential format, similar to a comic strip 
            # or animated storyboard, to optimize learning through dual visual and narrative engagement."

            # 5. Prompt: "Formulate a visually-centric story outline that mirrors a comic strip or animated sequence, 
            # leveraging the synergy of images and text to bolster memory retention."


            # 1. Prompt: "As a storyboarding expert, imagine you're creating a visual narrative for a complex tale. 
            # Your task is to design a series of illustrations that mimic a comic strip or animated sequence. 
            # Remember, the goal is to engage both visual and narrative elements simultaneously to enhance memory 
            # retention. Show, don't just tell; make every frame count in conveying the story's progression."

            # 2. Prompt: "Assume the role of an educational designer tasked with improving comprehension and recall 
            # for a dense narrative. You're to craft a visually-driven sequence resembling a comic strip or animated 
            # storyboard. Your challenge is to leverage the power of sequential imagery, ensuring each panel 
            # contributes to the overall understanding and recollection of the story."

            # 3. Prompt: "In the context of creating an immersive learning experience, you're a storyboarding artist 
            # commissioned to visually narrate a detailed story. Your action is to design a series of illustrations in 
            # a comic strip or animated format. The tone should be engaging and the experiment smart, focusing on how 
            # each visual element complements the narrative to improve understanding and memory retention."

            # 4. Prompt: "You're a creative storyboarding specialist tasked with optimizing learning through dual 
            # visual and narrative engagement. Your action is to generate a visual representation of a story in a 
            # sequential format, similar to a comic strip or animated sequence. The context is educational, and your 
            # experiment should focus on how each illustration contributes to the overall narrative and memory 
            # retention."

            # 5. Prompt: "Imagine you're a storyboarding artist working on a project to enhance memory retention using 
            # visual narratives. Your role is to formulate a visually-centric story outline that mirrors a comic strip 
            # or animated sequence. The action is to ensure every panel synergizes with the text to bolster 
            # understanding and recall, maintaining an engaging and vibrant tone throughout your creation."

        self.system_prompt = {
            "role": "system",
            "content": ("Develop a comprehensive storyboard for a complex narrative, incorporating visual elements to boost comprehension and recall.")
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
