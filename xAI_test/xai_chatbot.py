import gradio as gr
from typing import List, Tuple
import os
import requests
import json 
import time

API_KEY = os.getenv('XAI_API_KEY')

def get_llm_response(message: str) -> str:
    """
    Placeholder function for LLM API call.
    Replace this with your actual API implementation.
    """
    start = time.perf_counter()

    try:
        url = 'https://api.x.ai/v1/chat/completions'
        
        headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
                }
        
        data = {
                "messages": [
                    {
                    "role": "system",
                    "content": "You are Grok, a helpful assistant who answers questions."
                    },
                    {
                    "role": "user",
                    "content": message
                    }
                ],
                "model": "grok-beta",
                "stream": False,
                "temperature": 0
                }

        response = requests.post(url, headers=headers, json=data)
        end = time.perf_counter()

        print(json.dumps(response.json(), indent=4))

       # Extract the assistant's message from the response
        if isinstance(response, dict):  # If response is already a dictionary
            assistant_message = response['choices'][0]['message']['content']
        else:  # If response is a requests.Response object
            response_data = response.json()
            assistant_message = response_data['choices'][0]['message']['content']
            usage = response_data['usage']
            
        return assistant_message + '\n\n\n' + f'<small>API response time: {round(end - start)}'  + ' seconds' + f'\nUsage: {usage} </small>'
            
    except Exception as e:
        return f"Error: {str(e)}"

def chat_response(message: str, history: List[Tuple[str, str]]) -> str:
    """
    Process incoming messages and maintain chat history.
    """
    if not message:
        return ""
    
    # Get response from LLM
    response = get_llm_response(message)
    
    return response

# Create the Gradio interface
def create_chatbot():
    # Custom CSS for better appearance
    custom_css = """
    .chatbot-container {
        max-width: 800px;
        margin: auto;
    }
    """
    
    # Create the chat interface
    chat_interface = gr.ChatInterface(
        fn=chat_response,
        title="xAI Chatbot",
        description="A chatbot developed with XAI API.",
        examples=["What is machine learning?", 
                 "Write a poem about fall", 
                 "Suggest some theme ideas for a website"],
        theme="soft",
        css=custom_css
    )
    
    return chat_interface

if __name__ == "__main__":
    # Create and launch the chatbot
    chatbot = create_chatbot()
    chatbot.launch(
        server_name="0.0.0.0",  # Makes the app accessible on the network
        server_port=7860,       # Default Gradio port
        share=True              # Creates a public link
    )