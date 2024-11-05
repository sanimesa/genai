#create a class that can be instantiated by a client UI app. 
# This class should get a config as a parameter and then create a model handler and an SQL handler. 
# It should expose a method for generating SQL and another for executing SQL.

import yaml
import pathlib
import os
import re
from dotenv import load_dotenv
from handlers.gemini_handler import GeminiHandler
from handlers.openai_handler import GPT4Handler
from handlers.bigquery_handler import BigQueryUtils


load_dotenv()

class AppDriver:
    def __init__(self, config_path: str):
        self.load_config(config_path)

        #load the data configurattion
        self.data_config = self.load_data_config(config_path)

        #load the model and model configuration 
        self.model_handler = self.create_model_handler()
        # self.sql_handler = SQLHandler(self.config['sql_config'])
        # system_instruction = self.data_config.get('system_instructions')
        self.model_handler.configure(self.data_config)

        #hardcode bigquery for now 
        self.sql_handler = BigQueryUtils()

    def load_config(self, config_path: str):
        with open(config_path / 'config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        # Access the 'general_settings' section
        general_settings = self.config.get("general_settings", {})

    def load_data_config(self, config_path: str):
        settings = self.config['general_settings']
        data_source = settings['data_source']

        data_config = self.config['data_sources'].get(data_source)
        schema = data_config.get('schema')
        examples = data_config.get('examples')
        system_instruction = data_config.get('system_instruction')

        print(schema, examples, system_instruction)

        try:
            with open(config_path / schema, 'r') as f:
                schema_text = f.read()
                # print(schema_text)

            with open(config_path / examples, 'r') as f:
                example_text = f.read()
                print(example_text)

        except Exception as e:
            print(f"Error reading data source config files: {e}")


        return {
            "system_instructions": system_instruction,
            "schema": schema_text,
            "examples": example_text
        }

    def create_model_handler(self):
        settings = self.config['general_settings']
        model_type = settings['model_type']
        llms = self.config['model_config']

        if model_type == 'Gemini':
            return GeminiHandler(llms.get('Gemini'))
        elif model_type == 'gpt4':
            return GPT4Handler(llms.get('GPT'))
        else:
            raise ValueError(f"Invalid model type: {model_type}")
        
    def generate_sql(self, question, history=None):
        self.model_handler.start_chat(history)
        sql = self.model_handler.send_message(question)
        print(sql)

        pattern = r'```sql(.*?)```'
        matches = re.findall(pattern, sql, re.DOTALL)

        return matches[0]

    def execute_sql(self, sql):
        result = self.sql_handler.execute_sql(sql)
        return result

    def ask_llm(self, question: str) -> str:
        try:
            sql =  self.generate_sql(question)
            results = self.execute_sql(sql)
            return (sql, results)
        except Exception as e:
            print(f"An error has occured, str(e) ", "")    
            return (f"An error has occured, str(e) ", "")