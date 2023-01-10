from vk_parser import vk_session_group, vk, exception_handler, show_parsing_state, vk_session_group, log_parser
from .vkscript import execute
import re
import random
import sys


log_parser = log_parser()

class Deep_likes():
    def __init__(self):
        self.vk = vk

    def collect_posts(self, peer_id: int, group_ids: list):

        for group_id in group_ids:
            stop_parsing = show_parsing_state()
            if stop_parsing:
                print('stopped')
                break

            try:
                if self.vk.groups.getById(group_id=re.sub('-', '', str(group_id)))[0][
                    'is_closed'] != 0:
                    if self.vk.groups.getById(group_id=re.sub('-', '', str(group_id)))[0][
                        'is_member'] != 1:
                        log_parser.error(f'Бот не член этой группы {group_id}, а группа закрытая.')
                        continue

                count_value = self.vk.wall.get(owner_id=group_id)['count']
                response = execute(vk=self.vk, count=99, method='wall.get', offset_delta=100,
                                   owner_id=group_id, requests_num=15, limit=count_value)
                for id in response:
                    yield {'post_id': id, 'owner_id': group_id}

                if group_id == group_ids[-1]:
                    vk_session_group.method('messages.send', {'user_id': peer_id, 'message': 'Сканирование окончено',
                                                              'random_id': random.randrange(99999999)})

            except Exception as err:
                self.vk = exception_handler(err=err, except_location=sys._getframe().f_code.co_name,
                                            owner_id=group_id, peer_id=peer_id, vk=self.vk)

    def likes_downloader(self, group_ids: list, peer_id: int, searched_id: int):

        inspected_items = self.collect_posts(group_ids=group_ids, peer_id=peer_id)

        for item in inspected_items:
            try:
                res = self.vk.likes.getList(type='post', item_id=item['post_id'], owner_id=item['owner_id'], extended=1)

                for liker in res['items']:

                    if liker['id'] == searched_id:
                        yield {'liker_id': liker['id'], 'post_id': item['post_id'], 'owner_id': item['owner_id']}

            except Exception as err:
                self.vk = exception_handler(err, except_location=sys._getframe().f_code.co_name,
                                            owner_id=item['owner_id'], vk=self.vk, peer_id=peer_id)


    def send_result(self, group_ids: list, peer_id: int, searched_id: int):
        # Проверка, является ли бот членом группы.
        # Надо сделать проверку, является ли другом.
        results = self.likes_downloader(group_ids=group_ids, peer_id=peer_id, searched_id=searched_id)

        for result in results:

            name_of_group = vk_session_group.method('groups.getById', {'group_id': re.sub('-', '', str(result['owner_id']))})[0][
                'name']

            message = f'Лайк в группе {name_of_group} \n' \
                      f'Ссылка(если паблик):' \
                      f'https://vk.com/public{re.sub("-", "", result["owner_id"])}?w=wall{result["owner_id"]}_{result["post_id"]}\n' \
                      f' Ссылка(если группа):' \
                      f'https://vk.com/club{re.sub("-", "", result["owner_id"])}?w=wall{result["owner_id"]}_{result["post_id"]}'

            vk_session_group.method('messages.send', {'user_id': peer_id, 'message': message,
                                     'random_id': random.randint(0, 10000)})
