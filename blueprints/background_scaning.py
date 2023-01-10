import random
import threading
from vkbottle.bot import Blueprint
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle import StatePeer
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from models import *
from vk_parser.Daemon_comments_finder import Daemon_Comments_finder
from vk_parser import allow_parsing_thread, stop_parsing_thread
from STATES import BACKGROUND_COMMENTS
from start_keyboard import start_keyboard
import re

bp = Blueprint("for chat commands")
Admin_panel_db = Admin_panel_db()
Daemon_Comments_finder = Daemon_Comments_finder()

class MyRule(ABCRule[Message]):

    async def check(self, message: Message) -> bool:

        state = await bp.state_dispenser.get(message.peer_id)

        if isinstance(state, StatePeer):
            if state.state == 'BACKGROUND_COMMENTS:0'\
                    or state.state == 'BACKGROUND_COMMENTS:1':
                return True
            else:
                return False

@bp.on.message(MyRule())
async def handle_events(message: Message):

    page_number = Admin_panel_db.fetch_page_number()
    state = await bp.state_dispenser.get(message.peer_id)

    if message.text == 'Вперёд':
        page_number += 1
        Admin_panel_db.set_page_number(page_number)

        if page_number > 0:
            if state.state == 'BACKGROUND_COMMENTS:0':
                await choose_item(message)
            elif state.state == 'BACKGROUND_COMMENTS:1':
                await choose_word(message)

    elif message.text == 'Назад':
        page_number -= 1
        Admin_panel_db.set_page_number(page_number)
        if page_number >= 0:
            if state.state == 'BACKGROUND_COMMENTS:0':
                await choose_item(message)
            elif state.state == 'BACKGROUND_COMMENTS:1':
                await choose_word(message)

        else:
            Admin_panel_db.clear_buffer()
            Admin_panel_db.set_page_number(0)

            await bp.state_dispenser.delete(message.peer_id)
            await scaning_finished(message)


    elif message.text == 'Окончить выбор':
        Admin_panel_db.set_page_number(0)

        #Цифры ни на что не влияют, просто фреймфорк по неизвестной причине не принимает буквы в пейлоаде
        if message.payload == '986756493875334':

            await bp.state_dispenser.set(message.peer_id, BACKGROUND_COMMENTS.CHOOSE_WORD)
            await choose_word(message)

        elif message.payload == '9584756385938523':

            await bp.state_dispenser.set(message.peer_id, BACKGROUND_COMMENTS.LOAD_CHOICE)
            await comments_preloading(message)
    else:
            await is_button_clicked(message)



async def is_button_clicked(message: Message):
    state = await bp.state_dispenser.get(message.peer_id)
    fetched_buttons = Admin_panel_db.fetch_buttons(state.state)
    fetched_values = Admin_panel_db.fetch_values(state.state)
    if state.state == 'BACKGROUND_COMMENTS:0':

        isUniq_target = message.payload not in [button for button in fetched_buttons]

        if not isUniq_target:
            await message.answer(f"Нельзя выбрать одну группу или страницу несколько раз")
        else:
            text = f"Вы выбрали группу {message.text}" if str(message.payload)[0] == '-' else f"Вы выбрали страницу {message.text}"
            await message.answer(text)
            Admin_panel_db.save_button(message.payload, state.state)

    else:
        isUniq_word = message.text not in [value for value in fetched_values]

        if not isUniq_word:
            await message.answer(f"Нельзя выбрать одно слово несколько раз")
        else:
            await message.answer(f"Вы выбрали слово {message.text}")
            Admin_panel_db.save_value(message.text, state.state)



@bp.on.message(lev='Фоновое сканирование комментов')
async def choose_item(message: Message):

    state = await bp.state_dispenser.get(message.peer_id)

    if not state:
        page_number = 0
        Admin_panel_db.clear_buffer()
        await bp.state_dispenser.set(message.peer_id, BACKGROUND_COMMENTS.CHOOSE_GROUP)

    else:
        page_number = Admin_panel_db.fetch_page_number()


    all_groups = [f'-{group_id}' for group_id in Admin_panel_db.fetch_all_groups()] #маркируются группы, чтобы дифференцировать их от страниц юзеров
    all_users_pages = [user_id for user_id in Admin_panel_db.fetch_all_users_ids()]


    targets = all_groups + all_users_pages
    buttons = targets[0 + (page_number * 6): ((page_number + 1) * 6)]



    keyboard = Keyboard()
    for count, button in enumerate(buttons):
        filtered_target_ids = await bp.api.groups.get_by_id(group_id=re.sub("-", "", button)) if str(button)[0] == '-' else \
            await bp.api.users.get(user_ids=[button])
        name = filtered_target_ids[0].name if str(button)[0] == '-'\
            else f'{filtered_target_ids[0].first_name} {filtered_target_ids[0].last_name}'
        if count == 0:

            keyboard.row()
            keyboard.add(Text(f'{name}', f'{button}'))

        elif count % 2 == 0:
            keyboard.row()
            keyboard.add(Text(f'{name}', f'{button}'))
        else:
            keyboard.add(Text(f'{name}', f'{button}'))

    keyboard.row()
    keyboard.add(Text('Назад'), KeyboardButtonColor.PRIMARY)
    keyboard.add(Text('Вперёд'), KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text('Окончить выбор', '986756493875334'), KeyboardButtonColor.POSITIVE)
    keyboard.get_json()


    await message.answer(
        message="Выберите что будете мониторить",
        keyboard=keyboard)



@bp.on.message(state=BACKGROUND_COMMENTS.CHOOSE_WORD)
async def choose_word(message: Message):

    state = await bp.state_dispenser.get(message.peer_id)

    if not state:
        page_number = 0
        await bp.state_dispenser.set(message.peer_id, BACKGROUND_COMMENTS.CHOOSE_GROUP)
    else:
        page_number = Admin_panel_db.fetch_page_number()


    all_words = Admin_panel_db.fetch_all_words()

    buttons = all_words[0 + (page_number * 6): ((page_number + 1) * 6)]

    keyboard = Keyboard()
    for count, button in enumerate(buttons):

        if count == 0:
            keyboard.row()
            keyboard.add(Text(f'{button}', f'{(page_number*6) + (count + 1)}'))
        elif count % 2 == 0:
            keyboard.row()
            keyboard.add(Text(f'{button}', f'{(page_number*6) + (count + 1)}'))
        else:
            keyboard.add(Text(f'{button}', f'{(page_number*6) + (count + 1)}'))


    keyboard.row()
    keyboard.add(Text('Назад'), KeyboardButtonColor.PRIMARY)
    keyboard.add(Text('Вперёд'), KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text('Окончить выбор', payload='9584756385938523'), KeyboardButtonColor.POSITIVE)

    keyboard.get_json()

    await message.answer(
        message="Выберите слова",
        keyboard=keyboard)



@bp.on.message(state=BACKGROUND_COMMENTS.LOAD_CHOICE)
async def comments_preloading(message: Message):


    kb = Keyboard()
    kb.add(Text('Запустить мониторинг'), KeyboardButtonColor.PRIMARY)
    kb.row()

    kb.add(Text('Завершить досрочно'), KeyboardButtonColor.NEGATIVE)

    result_targets = Admin_panel_db.fetch_buttons('BACKGROUND_COMMENTS:0')
    result_word_chosen = Admin_panel_db.fetch_values('BACKGROUND_COMMENTS:1')
    result_groups_chosen = [i for i in result_targets if str(i)[0] == '-']
    result_user_pages_chosen = [i for i in result_targets if str(i)[0] != '-']

    result_groups = ''
    for i in result_groups_chosen:
        filtered = await bp.api.groups.get_by_id(group_id=re.sub("-", "", str(i)))
        result_groups += f'{filtered[0].name}, '

    result_user_pages = ''

    for i in result_user_pages_chosen:

        filtered = await bp.api.users.get(user_ids=[i])
        result_user_pages += f'{filtered[0].first_name}  {filtered[0].last_name},'

    result_words = ''
    for i in result_word_chosen:
        result_words += f'{i}, '


    await bp.api.messages.send(message=f'Выбраны слова: {result_words}\n '
                                       f'\nГруппы: {result_groups}\n '
                                       f'\nПользователи:{result_user_pages}',
                               peer_id=message.peer_id,
                               random_id=random.randrange(100000000000000000000000), keyboard=kb.get_json())

    await bp.state_dispenser.set(message.peer_id, BACKGROUND_COMMENTS.WAITING_FOR_START)


@bp.on.message(state=BACKGROUND_COMMENTS.WAITING_FOR_START)
async def wait_for_start(message: Message):
    global thread
    kb = Keyboard().add(Text('Завершить'), KeyboardButtonColor.PRIMARY)

    target_ids = Admin_panel_db.fetch_buttons(script_part='BACKGROUND_COMMENTS:0')
    serched_words = Admin_panel_db.fetch_values(script_part='BACKGROUND_COMMENTS:1')
    Admin_panel_db.clear_buffer()

    thread = threading.Thread(target=Daemon_Comments_finder.make_replies, args=([i for i in target_ids],20000,
                                                                                        [i for i in serched_words], message.peer_id))
    if message.text == 'Завершить досрочно':
        await message.answer('Сканирование отменено')
        await bp.state_dispenser.delete(message.peer_id)
        await scaning_finished(message)

    elif message.text == 'Запустить мониторинг':
        allow_parsing_thread()
        thread.start()
        await bp.state_dispenser.set(peer_id=message.peer_id, state=BACKGROUND_COMMENTS.DEEP_WAITING)
        await message.answer('Сканирование начато.', keyboard=kb.get_json())

@bp.on.message(state=BACKGROUND_COMMENTS.DEEP_WAITING)
async def comments_loading(message: Message):
    if message.text == 'Завершить':
        stop_parsing_thread()
        thread.join()
        await message.answer('Сканирование отменено')
        await bp.state_dispenser.delete(message.peer_id)
        await scaning_finished(message)




async def scaning_finished(message: Message):

    await message.answer('Опять работа?', keyboard=start_keyboard)

