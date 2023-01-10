import logging

def log_parser():
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler('errors.log')
    handler.setFormatter(formatter)

    log_parser = logging.getLogger('vk_parser')
    log_parser.setLevel(logging.ERROR)
    log_parser.addHandler(handler)

    return log_parser

credentials = [{
    'login': '79582537602',
    'password': 'LUF1hxWm'
},
    {
    'login': '375295415732',
    'password': 't3UreWGU'
    },

{
    'login': '380672331845',
    'password': 'borisyaboris1971'
    },
]

public_token = 'vk1.a.9UwgqS1iUbFEurlRH_gcVFwx9LdtkahTF7zNux8rXgXGRPlOHzCKMEHTp7Y' \
               's9Hzc1RZeQFgxNgVC9qreTv_1xU80Mj8kjPD6nNWFia8nCluOM227kHzZUddJ5sUO75-' \
               'rJOgvB3vX7B90VM6XgJ-FYpuyFr0zuchZPGUcZyya9ADoCZBl0noE8QDk3K2_IYAn'

