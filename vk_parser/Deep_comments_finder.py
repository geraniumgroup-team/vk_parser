from config import log_parser
from vk_parser import vk_session_group, vk, exception_handler, show_parsing_state
from .vkscript import execute
from models import Parser_DB
import re
import random
import sys

log_parser = log_parser()
Parser_DB = Parser_DB()


class Comments_finder():

    def __init__(self):
        self.vk = vk

    def collect_posts(self, peer_id: int, group_ids: list):

        for group_id in group_ids:
            stop_parsing = show_parsing_state()
            if stop_parsing:
                break

            try:
                count_value = self.vk.wall.get(owner_id=group_id)['count']

                response = execute(self.vk, count=99, method='wall.get', offset_delta=100,
                                   owner_id=group_id, requests_num=15, limit=count_value)
                for id in response:
                   yield {'id': id, 'owner_id': group_id}

                if group_id == group_ids[-1]:
                    vk_session_group.method('messages.send', {'user_id': peer_id, 'message': 'Сканирование окончено',
                                                              'random_id': random.randrange(99999999)})

            except Exception as err:
                self.vk = exception_handler(err=err, except_location=sys._getframe().f_code.co_name,
                                            owner_id=group_id, peer_id=peer_id, vk=self.vk)


    def receive_data(self, group_ids: list, peer_id: int):

        for count, post in enumerate(self.collect_posts(group_ids=group_ids, peer_id=peer_id)):
            stop_parsing = show_parsing_state()
            if stop_parsing:
                break

            try:
                raw_comments = self.vk.wall.getComments(owner_id=post['owner_id'], post_id=post['id'], extended=1)
                if raw_comments:
                    for comm in raw_comments['items']:
                        if 'owner_id' in comm and 'post_id'in comm and 'from_id' in comm and 'text' in comm :
                            # избавление от ошибки, вылетающей по постам вк, созданным до изменения стены в 2013
                            yield [{'owner_id': comm['owner_id'],
                                   'post_id': comm['post_id'], 'from_id': comm['from_id'], 'text': comm['text']}]

                            if comm['thread']['count'] > 0:

                                doughter_comments = self.vk.wall.getComments(owner_id=comm['owner_id'],
                                                                        comment_id=comm['id'], extended=1)

                                yield [{'owner_id': comm['owner_id'], 'post_id': comm['post_id'],
                                        'from_id': item['from_id'], 'text': item['text']} for item in doughter_comments['items']]



            except Exception as err:
                self.vk = exception_handler(err, except_location=sys._getframe().f_code.co_name,
                                            owner_id=post['owner_id'], peer_id=peer_id, vk=self.vk)



    def find_strings_in_comments(self, serched_items: list, group_ids: list, peer_id: int):
        for item in self.receive_data(group_ids=group_ids, peer_id=peer_id):
            for string in serched_items:
                res = re.findall(string.lower(), item[0]["text"].lower())

                if res:
                     yield {'owner_id': item[0]['owner_id'], 'post_id': item[0]['post_id'],
                           'from_id': item[0]['from_id'], 'text': item[0]['text']}





    def produce_replies_for_msg(self, searched_items: list, group_ids: list, peer_id: int):
        for result in self.find_strings_in_comments(serched_items=searched_items, group_ids=group_ids, peer_id=peer_id):
            stop_parsing = show_parsing_state()
            if stop_parsing:
                break

            finished_result = re.sub('-', '', str(result['owner_id']))
            group_name = vk.groups.getById(group_id=finished_result)

            user_name = vk.users.get(user_ids=result['from_id'])

            yield f"\n В группе «{group_name[0]['name']}» пользователь {user_name[0]['first_name']} {user_name[0]['last_name']} " \
                            f"https://vk.com/id{result['from_id']} написал коммент «{result['text']}»" \
                  f"Ссылка, если паблик:" \
                            f"https://vk.com/public{finished_result}?" \
                  f"w=wall{result['owner_id']}_{result['post_id']}\n" \
                  f"Ссылка, если группа: " \
                  f"https://vk.com/club{finished_result}?" \
                  f"w=wall{result['owner_id']}_{result['post_id']}\n"





    def go_search(self, peer_id:int, serched_items: list, group_ids: list):
        for finishing_result in self.produce_replies_for_msg(group_ids=group_ids, searched_items=serched_items,
                                                             peer_id=peer_id):
            stop_parsing = show_parsing_state()
            if stop_parsing:
                print('stopped')
                break

            try:
                if finishing_result:
                    vk_session_group.method('messages.send',
                                            {'user_id': peer_id, 'message': finishing_result,
                                             'random_id': random.randint(0, 10000)})

            except Exception as err:
                self.vk = exception_handler(err=err, except_location=sys._getframe().f_code.co_name, peer_id=peer_id, vk=self.vk)




class Comments_finder_on_people(Comments_finder):

    def __init__(self):
        super().__init__()

    def find_users_comments(self, searched_ids: list, group_ids: list, peer_id: int):
        for item in self.receive_data(group_ids=group_ids, peer_id=peer_id):
            stop_parsing = show_parsing_state()
            if stop_parsing:
                break

            for user_id in searched_ids:

                if str(item[0]['from_id']) == str(user_id):

                    result_comms = {'owner_id': item[0]['owner_id'],
                                     'post_id': item[0]['post_id'], 'from_id': item[0]['from_id'],
                                     'text': item[0]['text']}

                    if result_comms:
                        yield result_comms

    def produce_replies_for_msg(self, searched_items: list, group_ids: list, peer_id: int):
        for result in self.find_users_comments(searched_ids=searched_items, group_ids=group_ids, peer_id=peer_id):
            stop_parsing = show_parsing_state()
            if stop_parsing:
                break

            finished_owner_id = re.sub('-', '', str(result['owner_id']))
            group_name = vk.groups.getById(group_id=finished_owner_id)
            user_name = vk.users.get(user_ids=result['from_id'])
            finish_string = f"\n В группе «{group_name[0]['name']}» пользователь {user_name[0]['first_name']} {user_name[0]['last_name']} " \
                            f"Ссылка: \n" \
                            f"https://vk.com/id{result['from_id']} написал коммент «{result['text']}»" \
                            f"https://vk.com/public{finished_owner_id}?w=wall{result['owner_id']}_{result['post_id']}%2Fall\n"\
                            f"Ссылка, если группа: " \
            f"https://vk.com/club{finished_owner_id}?" \
            f"w=wall{result['owner_id']}_{result['post_id']}%2Fall\n"

            if finish_string:
                yield finish_string

    def go_search(self, peer_id: int, serched_items: list, group_ids: list):
        for finishing_result in self.produce_replies_for_msg(group_ids=group_ids, searched_items=serched_items,
                                                             peer_id=peer_id):
            stop_parsing = show_parsing_state()
            if stop_parsing:
               break

            try:
                if finishing_result:
                    vk_session_group.method('messages.send',
                                            {'user_id': peer_id, 'message': finishing_result,
                                             'random_id': random.randint(0, 10000)})
                else:

                    vk_session_group.method('messages.send',
                                            {'user_id': peer_id, 'message': 'Поиски не дали результата',
                                             'random_id': random.randint(0, 10000)})

            except Exception as err:
                self.vk = exception_handler(err=err, except_location='Sending_message', peer_id=peer_id, vk=self.vk)

