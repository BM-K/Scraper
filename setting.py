import logging
from argparse import ArgumentParser

class Arguments():
    def __init__(self):
        self.parser = ArgumentParser()

    def add_type_of_processing(self):
        self.add_argument('--scraping_task', type=str, default='jtbc')
        self.add_argument('--path_to_data', type=str, default='jtbc_data')
        self.add_argument('--latest_config', type=str, default='config.json')

    def add_argument(self, *args, **kw_args):
        return self.parser.add_argument(*args, **kw_args)

    def print_args(self, args):
        for idx, (key, value) in enumerate(args.__dict__.items()):
            if idx == 0:
                print("argparse{\n", "\t", key, ":", value)
            elif idx == len(args.__dict__) - 1:
                print("\t", key, ":", value, "\n}")
            else:
                print("\t", key, ":", value)

    def parse(self):
        args = self.parser.parse_args()
        self.print_args(args)
        
        return args

class Setting():
    def set_logger(self):
        _logger = logging.getLogger()
        formatter = logging.Formatter(
            '[%(levelname)s] %(asctime)s [ %(message)s ] | file::%(filename)s | line::%(lineno)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        _logger.addHandler(stream_handler)
        _logger.setLevel(logging.DEBUG)
        
        return _logger

    def run(self):
        parser = Arguments()
        parser.add_type_of_processing()

        args = parser.parse()
        
        return args
