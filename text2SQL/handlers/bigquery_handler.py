import os
import sys
import io
import json
import traceback 
import pandas as pd 
from google.cloud import bigquery

class BigQueryUtils: 

    def __init__(self):
        client = bigquery.Client()

    def execute_sql(self, source_query) -> str:
        df = pd.read_gbq(source_query)

        return df.to_csv()

def main():
    utils = BigQueryUtils()

    # query = """
    #     SELECT
    #         product_name, product_retail_price
    #     FROM
    #         `bigquery-public-data.thelook_ecommerce.inventory_items`
    #     ORDER BY
    #     product_retail_price DESC
    #     LIMIT 1
    #     """

    # print(utils.execute_sql(query))


if __name__ == "__main__":
	#set up logging 
	try:
		main()
	except Exception as exception:
		traceback.print_exception(*sys.exc_info())
