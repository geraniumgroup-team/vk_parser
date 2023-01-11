import requests
import io
from .auth_vk import vk_session_group
import time
import random


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

