from .model_handler import LLMHandler
import openai
import os

class GPT4Handler(LLMHandler):
    def __init__(self, config):
        self.config = config

    def configure(self):
        api_key = os.environ.get(self.config['api_key_env'])
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        openai.api_key = api_key

    def start_chat(self, system_instruction, history=None):
        self.system_instruction = system_instruction
        self.history = history or []

    def send_message(self, message):
        messages = [{"role": "system", "content": self.system_instruction}]
        for entry in self.history:
            messages.append({"role": entry["role"], "content": entry["parts"][0]})
        messages.append({"role": "user", "content": message})

        response = openai.ChatCompletion.create(
            model=self.config['model_name'],
            messages=messages,
            temperature=self.config['generation_config'].get('temperature', 0.7),
            max_tokens=self.config['generation_config'].get('max_tokens', 2048)
        )
        reply = response.choices[0].message.content
        return reply
