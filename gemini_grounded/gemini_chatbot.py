import gradio as gr
import google.generativeai as genai
from google.generativeai import types
import markdown2
import json
import os
from typing import Dict, List, Tuple

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def parse_gemini_response(response_data: types.GenerateContentResponse) -> Tuple[str, Dict[str, str]]:
    """
    Parse the Gemini API response to extract text and sources.
    
    Args:
        response_data: Raw response from Gemini API
    
    Returns:
        Tuple containing formatted text and sources dictionary
    """
    try:
        # Parse the response data
        
        # Extract the main text content
        text = response_data.text
        print("the text is: " + text)
        
        # Extract sources from grounding metadata
        sources = {}
        if "grounding_metadata" in response_data.candidates[0]:
            chunks = response_data.candidates[0].grounding_metadata.grounding_chunks
            for i, chunk in enumerate(chunks):
                if "web" in chunk:
                    source_name = chunk.web.title
                    source_url = chunk.web.uri
                    sources[f"source_{i+1}"] = {
                        "name": source_name,
                        "url": source_url
                    }
        
        return text, sources
    except Exception as e:
        return f"Error parsing response: {str(e)}", {}

def format_grouding_sources(content, citations):
    """
    Formats API response content and citations for Gradio chatbot.

    Args:
    - content (str): The main text.
    - citations (dict): A dictionary of sources with names and URLs.

    Returns:
    - str: A chatbot-formatted string with content and citations.
    """
    # Format the main text
    response = f"{content.strip()}\n\n"

    # Add citations section
    if len(citations) > 0: 
        response += "### Citations:\n"
        for key, source in citations.items():
            name = source.get('name', 'Unknown Source')
            url = source.get('url', '#')
            response += f"- [{name}]({url})\n"

    return response

def query_gemini(prompt: str, system_instruction: str, model: str, temperature: float, enable_search: bool = False) -> str:
    """
    Query the Gemini API with optional search grounding.
    
    Args:
        prompt: User input prompt
        use_grounding: Whether to enable search grounding
    
    Returns:
        Formatted response with citations if grounding was used
    """
    try:
        # Initialize Gemini model with appropriate configuration
        model = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": temperature,
                "top_p": 0.8,
                "top_k": 40
            },
            system_instruction=system_instruction,
            safety_settings=[],
        )

        response = model.generate_content(
            contents=prompt,
            tools={"google_search_retrieval": {
                "dynamic_retrieval_config": {
                    "mode": "unspecified",
                    "dynamic_threshold": 0.06}}})

        print(response)

        if enable_search:
            # Parse response and format with citations
            text, sources = parse_gemini_response(response)
            return format_grouding_sources(text, sources)
        else:
            # Return plain response
            return response.text
            
    except Exception as e:
        return f"Error generating response: {str(e)}"

def create_chatbot():
    # Define the theme
    theme = gr.themes.Base()
    
    with gr.Blocks(theme=theme, title="Gemini Chatbot") as app:
        gr.Markdown("# Gemini with Google Search Grounding")
        
        with gr.Row():
            # Left panel - Chat Interface
            with gr.Column(scale=2):
                # Chat history
                chat_history = gr.Chatbot(
                    height=500,
                    show_copy_button=True,
                    render_markdown=True,
                    container=True
                )
                
                # Input area below chat history
                with gr.Group():
                    chat_input = gr.Textbox(
                        placeholder="Type your message here...",
                        label="Message",
                        lines=3
                    )
                    
                    with gr.Row():
                        submit_btn = gr.Button("Submit", variant="primary")
                        clear_btn = gr.Button("Clear")
                
                # Examples
                gr.Examples(
                    examples=[
                        "What are the most recent features of BigQuery?",
                        "Write a haiku about fall season",
                        "Who won the US presidential election?"
                    ],
                    inputs=chat_input
                )
            
            # Right panel - Settings
            with gr.Column(scale=1):
                gr.Markdown("### Settings")
                
                model_selection = gr.Dropdown(
                    choices=["gemini-1.5-pro-002", "gemini-1.5-flash-002", "gemini-1.5-flash-8b"],
                    value="gemini-1.5-pro-002",
                    label="Model"
                )
                
                system_instruction = gr.Textbox(
                    value="You are a helpful assistant who answers questions. You have a search tool at your disposal to look up information.",
                    label="System Instructions",
                    lines=3
                )
                
                temperature = gr.Slider(
                    minimum=0,
                    maximum=1,
                    value=0,
                    step=0.1,
                    label="Temperature"
                )
                
                gr.Markdown("### Grounding")  # Added header for grounding section
                enable_search = gr.Checkbox(
                    label="Enable Search Grounding",
                    value=True,
                    info="When enabled, the model will use real-time search to ground its responses"
                )
        
        # Store conversation state
        state = gr.State([])
        
        def respond(message, history, system_inst, model, temp, search):
            if message:
                response = query_gemini(message, system_inst, model, temp, search)
                history.append((message, response))
                return "", history
            return "", history
        
        # Event handlers
        submit_btn.click(
            respond,
            inputs=[
                chat_input,
                chat_history,
                system_instruction,
                model_selection,
                temperature,
                enable_search
            ],
            outputs=[chat_input, chat_history]
        )
        
        chat_input.submit(
            respond,
            inputs=[
                chat_input,
                chat_history,
                system_instruction,
                model_selection,
                temperature,
                enable_search
            ],
            outputs=[chat_input, chat_history]
        )
        
        clear_btn.click(lambda: ([], None), outputs=[chat_history, chat_input])
    
    return app

if __name__ == "__main__":
    # Create and launch the chatbot
    app = create_chatbot()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )