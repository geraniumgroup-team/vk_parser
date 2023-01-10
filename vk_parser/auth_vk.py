from vk_parser import *
from config import credentials, public_token, log_parser
import vk_api
import time
import sys

attemp = 0

vk_session_group = vk_api.VkApi(token=public_token)

def auth():
    try:
        login = credentials[0]['login']
        password = credentials[0]['password']

        vk_session = vk_api.VkApi(login, password, app_id=2685278, client_secret="hHbJug59sKJie78wjrH8")
        vk_session.auth()
        vk = vk_session.get_api()
        return vk
    except Exception as err:
        time.sleep(5)
        from .exceptions import exception_handler
        exception_handler(err=err, except_location=sys._getframe().f_code.co_name, vk=None, peer_id=284359812)

def reauth(peer_id: int):
    global attemp

    try:
        attemp += 1

        if attemp > len(credentials) - 1:
            attemp = 0

        login = credentials[attemp]['login']
        password = credentials[attemp]['password']

        vk_session = vk_api.VkApi(login, password, app_id=2685278, client_secret="hHbJug59sKJie78wjrH8")
        vk_session.auth()
        vk = vk_session.get_api()
        print(f'Произошла переавторизация на логин {login}')
        log_parser().error(f'Произошла переавторизация на логин {login}')
        return vk

    except Exception as err:
        time.sleep(5)
        from .exceptions import exception_handler
        exception_handler(err=err, except_location=sys._getframe().f_code.co_name, vk=None, peer_id=peer_id)


