import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
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
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  system_instruction="You are a Google SQL expert. \n\nYou have been tasked to generate SQL statements to answer user questions based on the below schema:\n\nCREATE TABLE `bigquery-public-data.thelook_ecommerce.users`\n(\n  id INT64,\n  first_name STRING,\n  last_name STRING,\n  email STRING,\n  age INT64,\n  gender STRING,\n  state STRING,\n  street_address STRING,\n  postal_code STRING,\n  city STRING,\n  country STRING,\n  latitude FLOAT64,\n  longitude FLOAT64,\n  traffic_source STRING,\n  created_at TIMESTAMP\n);\n\nCREATE TABLE `bigquery-public-data.thelook_ecommerce.order_items`\n(\n  id INT64,\n  order_id INT64,\n  user_id INT64,\n  product_id INT64,\n  inventory_item_id INT64,\n  status STRING,\n  created_at TIMESTAMP,\n  shipped_at TIMESTAMP,\n  delivered_at TIMESTAMP,\n  returned_at TIMESTAMP,\n  sale_price FLOAT64\n);\n\nCREATE TABLE `bigquery-public-data.thelook_ecommerce.products`\n(\n  id INT64,\n  cost FLOAT64,\n  category STRING,\n  name STRING,\n  brand STRING,\n  retail_price FLOAT64,\n  department STRING,\n  sku STRING,\n  distribution_center_id INT64\n);\n\nHere are some examples:\n\nUser: Best Selling Item?\nAssistant:\nSELECT oi.product_id as product_id, p.name as product_name, p.category as product_category, count(*) as num_of_orders\nFROM `bigquery-public-data.thelook_ecommerce.products` as p \nJOIN `bigquery-public-data.thelook_ecommerce.order_items` as oi\nON p.id = oi.product_id\nGROUP BY 1,2,3\nORDER BY num_of_orders DESC;\n\nUser: Top 10 Customers by Average Order Price?\nAssistant: SELECT u.id as user_id, u.first_name, u.last_name, avg(oi.sale_price) as avg_sale_price\nFROM `bigquery-public-data.thelook_ecommerce.users` as u \nJOIN `bigquery-public-data.thelook_ecommerce.order_items` as oi\nON u.id = oi.user_id\nGROUP BY 1,2,3\nORDER BY avg_sale_price DESC\nLIMIT 10;",
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "Which user bought the most items?",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT u.id as user_id, u.first_name, u.last_name, COUNT(oi.id) AS total_items_bought\nFROM `bigquery-public-data.thelook_ecommerce.users` AS u\nJOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi\nON u.id = oi.user_id\nGROUP BY 1, 2, 3\nORDER BY total_items_bought DESC\nLIMIT 1;\n```",
      ],
    },
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)