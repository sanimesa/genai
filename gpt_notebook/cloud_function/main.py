import functions_framework
import json
import pandas as pd
from modules import gemini_helper
from modules import data_utils
from flask import jsonify

@functions_framework.http
def service(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    log_request_details(request)

    if request.method == 'GET':
        return jsonify(message='Not implemented!'), 405

    action = request.headers.get('X-Envoy-Original-Path', None)
    user_id = request.headers.get('Openai-Ephemeral-User-Id', None)

    if not action:
        return jsonify(message="Action not specified in the headers."), 400

    if not user_id:
        return jsonify(message="User ID not specified in the headers."), 400

    try:
        if action == '/store':
            return handle_store_action(request_json, user_id)
        elif action == '/retrieve':
            return handle_retrieve_action(request_json, user_id)
        else:
            return jsonify(message="Invalid request"), 400
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}"), 500

def log_request_details(request):
    print(f"Request args: {request.args}")
    print(f"Request headers: {request.headers}")
    if request.json:
        print(f"Request JSON: {json.dumps(request.json)}")

def handle_store_action(request_json, user_id):
    required_keys = ['topic', 'parsed_values', 'raw_text']
    if not all(key in request_json for key in required_keys):
        return jsonify(message="Missing required fields in the JSON body."), 400

    topic = request_json['topic']
    content = request_json['parsed_values']
    raw_text = request_json['raw_text']

    df = pd.DataFrame({'user_id': [user_id], 'topic': [topic], 'content': [content], 'raw_text': [raw_text]})
    result = data_utils.df_to_bq(df)

    if result:
        return jsonify(message="Content stored successfully!"), 200
    else:
        return jsonify(message="Failed to store content"), 500

def handle_retrieve_action(request_json, user_id):
    if 'query' not in request_json:
        return jsonify(message="Missing 'query' in the JSON body."), 400

    sql_query = gemini_helper.get_sql_query(request_json['query']).format(user_id=user_id)
    print(f"SQL Query: {sql_query}")
    df = data_utils.read_gbq(sql_query)

    return jsonify(message='Here are the relevant notes', data=df.to_json(orient='records')), 200
