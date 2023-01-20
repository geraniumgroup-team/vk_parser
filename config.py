import logging

def log_parser():
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler('errors.log')
    handler.setFormatter(formatter)

    log_parser = logging.getLogger('vk_parser')
    log_parser.setLevel(logging.ERROR)
    log_parser.addHandler(handler)

    return log_parser

credentials = [{]

public_token = ''

