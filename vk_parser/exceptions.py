from .captcha_handler import captcha_handler
from config import log_parser
from vk_api import exceptions
from vk_parser import reauth, vk_session_group
import vk_api
import time
import random
import re
import requests


log_parser = log_parser()
attemp = 0

def exception_handler(err, except_location: str, peer_id: int, vk, post_id = None, owner_id=None):
    global attemp
    if isinstance(err, exceptions.AuthError):

        vk_session_group.method('messages.send', {
            'message': f'Произошла ошибка в процессе авторизации {err}',
            'peer_id': peer_id,
            'random_id': random.randrange(100000000000)})

        log_parser.error(f'AuthError: {err}')

        vk = reauth(peer_id=peer_id)
        return vk

    else:
        owner = f'https://vk.com/public{re.sub("-", "", str(owner_id))} ' \
                f'https://vk.com/club{re.sub("-", "", str(owner_id))} или https://vk.com/id{owner_id}'
        vk_session_group.method('messages.send', {
            'message': f'Произошла ошибка в процессе работы: {err}. Место ошибки: {except_location}. '
                       f'По группе/странице: {owner} по посту: {post_id}',
            'peer_id': peer_id,
            'random_id': random.randrange(100000000000)})

        log_parser.error(f'{err} on group:{owner} on post {post_id}')

        if isinstance(err, requests.exceptions.ConnectionError):
            time.sleep(600)  # 10 минут сна хватает после кика от vk.com

            vk = reauth(peer_id=peer_id)
            return vk

        if isinstance(err, vk_api.exceptions.ApiError):

            if err.code == 29 or err.code == 10: #код ошибки мута
                time.sleep(900)
                vk = reauth(peer_id=peer_id)
                return vk

        elif isinstance(err, vk_api.Captcha):
            captcha_handler(err, peer_id)

    return vk




