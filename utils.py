import os
import json

from datetime import datetime

class Utils():
    def __init__(self, args):
        self.args = args
        self.data_path = f'{args.path_to_data}'
        self.config_path = f'{self.data_path}/{args.latest_config}'
        self.config = dict()

    def init_config_file(self
    ):
        os.makedirs(self.data_path)
        self.config['Last_file_name'] = 'init'
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def get_newest_config(self
    ):
        if not os.path.exists(self.data_path):
            self.init_config_file()

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return config

    def make_metadata(self
    ):
        last_update_time = datetime.now()
        file_count = len(os.listdir(self.args.path_to_data))

        return str(last_update_time), file_count

    def update_config(self,
                      key=None,
                      information=None
    ):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            last_update_time, file_count = self.make_metadata()

            self.config = {'Newspaper': self.args.scraping_task,
                           'Last_file_name': key.strip(),
                           'Current_data_count': len(information),
                           'Total_file_count': file_count+len(information)-1,
                           'Last_update_time': last_update_time}

            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def upload_data(self,
                    information=None
    ):
        for index, (key, value) in enumerate(information.items()):
            if index == 0:
                self.update_config(key, information)

            file_name = f'{self.data_path}/{key.strip()}.json'
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False, indent=4)

        self.print_log()

    def print_log(self):
        if len(self.config) == 0:
            print("Info: During the designated time period, no data was gathered.")
        else:
            print(self.config)
