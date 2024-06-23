import os
import pandas_gbq

project_id = os.environ.get('PROJECT_ID')
target_table = 'gpt_data.gpt_notebook_log'

# Save Pandas dataframe to BQ 
def df_to_bq(df, project_id=project_id, target_table=target_table, if_exists='append', schema=None):
    print(f'loading data into: {target_table} from dataframe')

    try:
        df.to_gbq(target_table, project_id=project_id, if_exists=if_exists, table_schema=schema)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# load data from BQ 
def read_gbq(source_query):
    print(f'loading data from: {source_query}')

    try: 
        df = pandas_gbq.read_gbq(source_query, project_id=project_id)

        return df
    except Exception as e:
        print(f"Error: {e}")
        return None