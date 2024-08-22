import os
import pandas as pd
import pandas_gbq
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('bigquery_service_account_file.json')

project_id, dataset_id = 'project_id', 'dataset_id'

source_folder = 'd:/folder_with_excel_file'
sheet_name = 'sheet_name'

files = os.listdir(source_folder)

print(files)

for file in files:
    file_name = file.split('.')[0]
    file_path = f'{source_folder}/{file}'
    table_id = f'{dataset_id}.{file_name}'

    df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str) # dtype=str все ячейки будут как текст считаны, иначе надо перечислять converters={'names':str,'ages':str}
    pandas_gbq.to_gbq(df, table_id, project_id=project_id, credentials=credentials, if_exists='replace')
    
    print(file_path, table_id)