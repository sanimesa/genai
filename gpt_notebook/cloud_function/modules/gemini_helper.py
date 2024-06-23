import os
import re
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"]) 

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="""
        Accept user queries in English and produce an SQL statement to retrieve data from a 
        BigQuery table with the below definition:
        
        CREATE TABLE gpt_data.gpt_notebook_log (
        id STRING DEFAULT GENERATE_UUID(), 
        user_id STRING,
        update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
        topic STRING, 
        content STRING,  raw_text STRING
        );
        
        Always append an additional where condition to the queries:
        user_id = '{user_id}'
        
        Make the queries compliant with Google SQL dialect. 
        If the user request can not be reliably translated, return \"More information needed\". 
        
        Example: 
        
        User: Please retrieve the reminders for the last two days. 
        Assistant: 
        
        SELECT update_time, topic, raw_text 
        FROM gpt_data.gpt_notebook_log 
        WHERE user_id = '{user_id}'
        AND topic = 'Reminder'
        AND update_time  > current_timestamp() - interval 2 day;""",
)


def get_sql_query(user_query):
  
    chat_session = model.start_chat(
        history=[
        ]
    )
  
    response = chat_session.send_message(user_query)
    print(response.text)

    sql_statement = re.search(r'```sql(.*?)```', response.text, re.DOTALL).group(1)

    return sql_statement

  
  
if __name__ == "__main__":
    print(get_sql_query("Please retrieve the reminders for the last two days."))
    print(get_sql_query("Please retrieve all notes."))
