import os
import json
import pandas as pd

news_dataset = ['jtbc_data', 'newsis_data', 'nocut_data', 'sbs_data']
config_file_name = 'config.json'

for news_data in news_dataset:
    meta_data = list()
    files = os.listdir(news_data)
    files_with_dir = [f'{news_data}/{file}' for file in files]

    for file in files_with_dir:
        if config_file_name in file: continue
        with open(file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

            date = json_data['date']
            category = json_data['category']
            title = json_data['title']
            writer = json_data['writer']
            email = json_data['writer_email']
            vision = json_data['vision']
            contents = json_data['contents']

            current_meta_data = [category, title, vision, contents, date, writer, email]
            meta_data.append(current_meta_data)

    index = [i+1 for i in range(len(files_with_dir)-1)]
    columns = ['category', 'title', 'vision', 'contents', 'date', 'writer', 'email']

    news_name = news_data.replace("_data", "")
    df = pd.DataFrame(meta_data, index=index, columns=columns)
    df.to_excel(f'{news_name}_metadata.xlsx', sheet_name=news_name)
