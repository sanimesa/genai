from .model_handler import LLMHandler
import google.generativeai as genai
import os

class GeminiHandler(LLMHandler):

    def __init__(self, config):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.config = config

    def configure(self, data_config: dict):
        # Create the model
        generation_config = self.config.get("generation_config")
        print(generation_config)

        schema = data_config.get('schema')
        examples = data_config.get('examples')
        system_instructions = data_config.get('system_instructions')

        system_prompt = f"""{system_instructions}
            {schema}
            Here are some examples:
            {examples}"""

        self.model = genai.GenerativeModel(
            model_name=self.config['model_name'],
            generation_config=generation_config,
            system_instruction=system_prompt
        )

        print(self.model)

    def start_chat(self, history=None):
        self.chat_session = self.model.start_chat(
            history=history
        )

    def send_message(self, message):
        response = self.chat_session.send_message(message)
        return response.text