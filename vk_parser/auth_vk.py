from vk_parser import *
from config import credentials, public_token, log_parser
import vk_api
import time
import sys
import requests
import io
import random

attemp = 0
vk_session_group = vk_api.VkApi(token=public_token)

def auth(peer_id: int):

    try:
        login = credentials[0]['login']
        password = credentials[0]['password']

        vk_session = vk_api.VkApi(login, password, app_id=2685278, client_secret="hHbJug59sKJie78wjrH8", captcha_handler=captcha_handler)
        vk_session.auth()
        vk = vk_session.get_api()
        return vk
    except Exception as err:
        time.sleep(5)
        from .exceptions import exception_handler
        exception_handler(err=err, except_location=sys._getframe().f_code.co_name, vk=None, peer_id=peer_id)

def reauth(peer_id: int):
    global attemp

    try:
        attemp += 1

        if attemp > len(credentials) - 1:
            attemp = 0

        login = credentials[attemp]['login']
        password = credentials[attemp]['password']

        vk_session = vk_api.VkApi(login, password, app_id=2685278, client_secret="hHbJug59sKJie78wjrH8",
                                  captcha_handler=captcha_handler)
        vk_session.auth()
        vk = vk_session.get_api()
        print(f'Произошла переавторизация на логин {login}')
        log_parser().error(f'Произошла переавторизация на логин {login}')
        return vk

    except Exception as err:
        time.sleep(5)
        from .exceptions import exception_handler
        exception_handler(err=err, except_location=sys._getframe().f_code.co_name, vk=None, peer_id=peer_id)

def captcha_handler(captcha, peer_id: int):
    captcha_url = captcha.get_url()

    # Сохраняем изображение капчи
    image_content = io.BytesIO(requests.get(captcha_url).content)
    image_content.seek(0)
    image_content.name = ('/home/barbus/Изображения/Снимки экрана/Снимок экрана от 2022-07-17 23-55-24.png')

    # Получаем адрес капчи
    url = vk_session_group.method('photos.getMessagesUploadServer')['upload_url']

    # Загружаем изображение на сервер ВКонтакте
    request = requests.post(url, files={'photo': image_content}).json()


    photo = vk_session_group.method('photos.saveMessagesPhoto',
                                    {'server': request['server'], 'photo': request['photo'], 'hash': request['hash']})

    attachment = 'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])


    time.sleep(1)

    # Отправляем сообщение
    vk_session_group.method('messages.send', {'user_id': peer_id, 'message': 'Введите и отправьте текст с капчи боту,'
                                                                              'чтобы он заработал',
                                              'attachment': attachment, 'random_id': random.randint(0, 10000)})

    # Ждем ответа
    key = ''
    while (key == ''):
        # Получаем первый в списке диалог
        # Если к сообщению не прикреплено изображение, то, значит, это ключ
        messages = vk_session_group.method('messages.getDialogs')['items'][0]
        time.sleep(5)
        if 'attachments' not in messages['message'].keys():
            key = messages['message']['body']

    # Отправляем ключ (текст) капчи
    return captcha.try_again(key)


