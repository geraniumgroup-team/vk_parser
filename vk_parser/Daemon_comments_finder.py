from config import log_parser
from vk_parser import vk_session_group, vk, exception_handler, show_parsing_state
from models import Parser_DB
import re
import random
import datetime
import time
import pytz
import sys

log_parser = log_parser()
Parser_DB = Parser_DB()

#Класс не использует VKscript, чтобы грамотно использовать лимит запросов, предоставляемый сервером vk.com
class Daemon_Comments_finder():
    def __init__(self):
        self.sleep = 0.0001
        self.amount_posts = 0
        self.vk = vk

    def post_finder(self, targets_ids: list, limit: int, peer_id: int):
        general_cont = 0

        while not show_parsing_state():

            general_cont += 1
            stop_parsing = show_parsing_state()
            print(stop_parsing)
            if stop_parsing:
                 return

            if general_cont > 1:
                vk_session_group.method('messages.send', {
                    'message': f'Проверил все группы и страницы, захожу на новый круг №{general_cont}',
                    'peer_id': peer_id,
                    'random_id': random.randrange(1000000000)})
            for target_id in targets_ids:
                try:
                    vk_posts = self.vk.wall.get(owner_id=target_id, count=99)['items']

                    for count_post, post in enumerate(vk_posts):
                        stop_parsing = show_parsing_state()
                        if stop_parsing:
                             return

                        self.amount_posts += 1
                        time.sleep(self.sleep)

                        post_datetime = datetime.datetime.strptime(
                            datetime.datetime.utcfromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M:%S'),
                            '%Y-%m-%d %H:%M:%S')
                        moskow = pytz.timezone('Europe/Moscow')

                        #Проверка. Если пост старше limit(неделя по умолчанию), то он не мониторится. Таким образом задаётся
                        #глубина мониторинга: чтобы мониторились только актуальные комменты, а не все комменты группы, коих
                        #могут быть сотни тысяч.
                        if post_datetime.astimezone(moskow) >= datetime.datetime.now().astimezone(moskow) - datetime.timedelta(
                                days=limit):
                            if 'id' in post and 'owner_id' in post:
                                yield post['id'], post['owner_id'], post['text']
                            else:
                                log_parser.error(f'Обнаружен баганый пост без owner_id - {post}')
                        else:
                            break


                except Exception as err:
                    self.vk = exception_handler(err, except_location=sys._getframe().f_code.co_name, peer_id=peer_id, vk=self.vk)



    def comments_finder(self, targets_ids: list, limit: int, searched_strings: list, peer_id: int) -> dict:
        for post_id, owner_id, post_text in self.post_finder(targets_ids=targets_ids, limit=limit, peer_id=peer_id):

            stop_parsing = show_parsing_state()
            if stop_parsing:
                return
            #Поиск ключевых слов в теле поста
            #Заносим в кэш item_id со знаком "-" чтобы кэш поста не спутался с кэшем коммента, id которого может быть равен id поста
            for string in searched_strings:
                result = re.findall(string.lower(), post_text.lower())

                if result:
                    item_id = f'-{post_id}'
                    data = Parser_DB.fetch_cache(target_id=owner_id, post_id=post_id, item_id=item_id)

                    if data and (owner_id, post_id, int(item_id)) == data:
                        continue
                    else:
                        Parser_DB.add_cache(target_id=owner_id, post_id=post_id, item_id=item_id)
                        yield {'post_text_found':{'post_id': post_id, 'owner_id': owner_id, 'searched_string': string}}

            #Поиск узловых комментов поста(комменты поста, которые могут иметь дочерние комменты) и ключевых слов в них
            try:
                comments_nodes = self.vk.wall.getComments(owner_id=owner_id, post_id=post_id, extended=1)

                time.sleep(self.sleep)
                for comment in [row_comments for row_comments in comments_nodes['items']]:

                    stop_parsing = show_parsing_state()
                    if stop_parsing:
                       return

                    if comment:
                        for string in searched_strings:
                            res = re.findall(string.lower(), comment['text'].lower())
                            if res:
                                data = Parser_DB.fetch_cache(target_id=owner_id, post_id=post_id, item_id=comment['id'])

                                if data and (owner_id, post_id, comment['id']) == data:
                                   continue
                                else:
                                    Parser_DB.add_cache(target_id=owner_id, post_id=post_id, item_id=comment['id'])

                                    yield {'comment_found':{'owner_id': owner_id, 'post_id': post_id,
                                               'from_id': comment['from_id'],
                                               'text': comment['text']}}

                        #Поиск дочерних комментов узлового коммента и ключевых слов в них
                        if comment['thread']['count']:
                            try:
                                doughter_comments = self.vk.wall.getComments(owner_id=owner_id, comment_id=comment['id'],
                                                                        extended=1)
                                time.sleep(self.sleep)

                                for doughter_comment in doughter_comments['items']:

                                    stop_parsing = show_parsing_state()
                                    if stop_parsing:
                                        return

                                    for string in searched_strings:
                                        res = re.findall(string.lower(), doughter_comment['text'].lower())
                                        if res:
                                            data = Parser_DB.fetch_cache(target_id=owner_id, post_id=post_id, item_id=doughter_comment['id'])

                                            if data and (owner_id, post_id, doughter_comment['id']) == data:
                                                continue
                                            else:
                                                Parser_DB.add_cache(target_id=owner_id, post_id=post_id, item_id=doughter_comment['id'])

                                                yield {'comment_found':{'owner_id': owner_id, 'post_id': post_id,
                                                        'from_id': doughter_comment['from_id'],
                                                        'text': doughter_comment['text']}}
                            except Exception as err:
                                self.vk = exception_handler(err, except_location='Doughter comments',
                                                            owner_id=owner_id, peer_id=peer_id, vk=self.vk)
            except Exception as err:
                self.vk = exception_handler(err, except_location=sys._getframe().f_code.co_name, peer_id=peer_id, vk=self.vk)


    def make_replies(self, targets_ids: list, limit: int, searched_strings: list, peer_id: int):
        Parser_DB.clear_cache() #Удаление кэша. Кэш нужен, чтобы не выдавать один и тот же результат много раз

        for item in self.comments_finder(targets_ids, limit, searched_strings, peer_id=peer_id):
            stop_parsing = show_parsing_state()
            if stop_parsing:
               return
            # try:
            if 'post_text_found' in item:
                finish_owner_id = re.sub('-', '', str(item['post_text_found']['owner_id']))
                #Посты групп начинаются на "-", посты пользователей не имеют этого знака.
                if str(item['post_text_found']['owner_id'])[0] == '-':
                    group_name = self.vk.groups.getById(group_id=finish_owner_id)[0]['name']
                    text_part = f"\n В посте группы «{group_name}»"
                    prefix = 'https://vk.com/public'
                    extra_message = f"Ссылка(если группа): https://vk.com/club{finish_owner_id}" \
                                    f"?w=wall-{finish_owner_id}_{item['post_text_found']['post_id']}\n "

                else:
                    user_name = self.vk.users.get(user_ids=[finish_owner_id])
                    text_part = f"\n В посте на странице пользователя «{user_name[0]['first_name']}{user_name[0]['last_name']}» "
                    prefix = 'https://vk.com/id'
                    extra_message = ''

                vk_session_group.method('messages.send',
                                        {'message': f'{text_part}'
                                                    f' найдено слово {item["post_text_found"]["searched_string"]} '
                                                    f'{prefix}{finish_owner_id}'
                                                    f'?w=wall{finish_owner_id}_'
                                                    f'{item["post_text_found"]["post_id"]}%2Fall\n '
                                                    f' {extra_message}'
                                                    f' Всего постов проверено: {self.amount_posts}', 'peer_id': peer_id,
                                         'random_id': random.randrange(100000000000000)})


            else:
                finish_owner_id = re.sub('-', '', str(item['comment_found']['owner_id']))
                # Посты групп начинаются на "-", посты пользователей не имеют этого знака.
                if str(item['comment_found']['owner_id'])[0] == '-':
                    post_id = item['comment_found']['post_id']
                    group_name = self.vk.groups.getById(group_id=finish_owner_id)[0]['name']
                    text_part = f"\n В паблике «{group_name}»"
                    prefix = 'https://vk.com/public'
                    extra_message = f"Ссылка(если группа): https://vk.com/club{finish_owner_id}" \
                                    f"?w=wall-{finish_owner_id}_{post_id}"

                else:
                    user_name = self.vk.users.get(user_ids=[finish_owner_id])
                    text_part = f"\n На странице пользователя «{user_name[0]['first_name']}{user_name[0]['last_name']}» "
                    prefix = "https://vk.com/id"
                    extra_message = ''

                commentator_id = item['comment_found']['from_id']
                user_name = self.vk.users.get(user_ids=item['comment_found']['from_id'])
                commentator_name_first_name = user_name[0]['first_name'] if user_name else 'Админ группы'
                commentator_name_last_name = user_name[0]['last_name'] if user_name else 'Или удалённая страница'
                comment_text = item['comment_found']['text']
                vk_session_group.method('messages.send', {'message': f"\n{text_part}"
                                                                     f"пользователь {commentator_name_first_name} {commentator_name_last_name} " 
                                                                     f"https://vk.com/id{commentator_id} написал коммент: «{comment_text}» "
                                                                     f"Ссылка: {prefix}{finish_owner_id}"
                                                                     f"?w=wall-{finish_owner_id}_"
                                                                     f"{item['comment_found']['post_id']}"
                                                                     f" {extra_message}"
                                                                     f" Всего постов проверено: {self.amount_posts}",
                                                          'peer_id': peer_id,
                                                          'random_id': random.randrange(100000000000)})

            # except Exception as err:
            #
            #     self.vk = exception_handler(err, except_location=sys._getframe().f_code.co_name, peer_id=peer_id, vk=self.vk)
