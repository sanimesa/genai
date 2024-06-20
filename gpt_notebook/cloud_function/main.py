import functions_framework
import json 
import os

project_id = os.environ.get('GCP_PROJECT')
print(f'project_id: {project_id}')

def df_to_bq(df, project_id, target_table, if_exists='append', schema=None):
    print(f'loading data into: {target_table} from dataframe')

    print(df.head)
    print(df.info())
    # Save Pandas dataframe to BQ 
    df.to_gbq(target_table, project_id=project_id, if_exists=if_exists, table_schema=schema)

@functions_framework.http
def service(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args


    if request.method == 'GET':
        if request_json and 'name' in request_json:
            name = request_json['name']
        elif request_args and 'name' in request_args:
            name = request_args['name']
        else:
            name = 'World'
        return 'Hello {}!'.format(name)
    else:
        response_str = f"Request details: {request.path=} {request.method=} {json.dumps(request_json)}"
        print(response_str)
        print(request.headers)
        return response_str
