import random
import threading
from vkbottle.bot import Blueprint
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle import StatePeer
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from models import Admin_panel_db
from STATES import DEEP_SCAN_COMMENTS
from start_keyboard import start_keyboard
from vk_parser.Deep_comments_finder import Comments_finder, Comments_finder_on_people
from vk_parser import stop_parsing_thread, allow_parsing_thread

bp = Blueprint("for chat commands")
Admin_panel_db = Admin_panel_db()


class MyRule(ABCRule[Message]):
    async def check(self, message: Message) -> bool:
        state = await bp.state_dispenser.get(message.peer_id)

        if isinstance(state, StatePeer):
            if state.state == 'DEEP_SCAN_COMMENTS:1'\
                    or state.state == 'DEEP_SCAN_COMMENTS:2' \
                    or state.state == 'DEEP_SCAN_COMMENTS:3':
                return True
            else:
                return False


@bp.on.message(MyRule())
async def handle_callback_event(message: Message):

    page_number = Admin_panel_db.fetch_page_number()
    state = await bp.state_dispenser.get(message.peer_id)

    if message.text == 'Вперёд':
        page_number += 1
        Admin_panel_db.set_page_number(page_number)
        if page_number > 0:
            if state.state == 'DEEP_SCAN_COMMENTS:1':
                await choose_item(message)
            elif state.state == 'DEEP_SCAN_COMMENTS:2':
                await choose_word(message)
            elif state.state == 'DEEP_SCAN_COMMENTS:3':
                await choose_user_ids(message)

    elif message.text == 'Назад':

        page_number -= 1
        Admin_panel_db.set_page_number(page_number)
        if page_number >= 0:
            if state.state == 'DEEP_SCAN_COMMENTS:1':
                await choose_item(message)
            elif state.state == 'DEEP_SCAN_COMMENTS:2':
                await choose_word(message)
            elif state.state == 'DEEP_SCAN_COMMENTS:3':
                await choose_user_ids(message)

        else:
            Admin_panel_db.clear_buffer()
            await bp.state_dispenser.delete(message.peer_id)
            Admin_panel_db.set_page_number(0)
            await comments_finished(message)


    elif message.text == 'Окончить выбор':
        # Цифры ни на что не влияют, просто фреймфорк по неизвестной причине не принимает буквы в пейлоаде
        Admin_panel_db.set_page_number(0)
        if message.payload == '986756493875334':

            await bp.state_dispenser.set(message.peer_id, DEEP_SCAN_COMMENTS.CHOOSE_WORD)
            await choose_word(message)

        elif message.payload == '986756493875335':

            await bp.state_dispenser.set(message.peer_id, DEEP_SCAN_COMMENTS.CHOOSE_USERS_IDS)
            await choose_user_ids(message)

        elif message.payload == '9584756385938523': #CHOOSE_Words

            await bp.state_dispenser.set(message.peer_id, DEEP_SCAN_COMMENTS.LOAD_CHOICE)
            await comments_preloading(message)

        elif message.payload == '9584756385938524': #CHOOSE_ids

            await bp.state_dispenser.set(message.peer_id, DEEP_SCAN_COMMENTS.LOAD_CHOICE)
            await comments_preloading(message, scan_on_people=True)

    else:
        await is_button_clicked(message)



async def is_button_clicked(message: Message):

    state = await bp.state_dispenser.get(message.peer_id)
    if state.state == 'DEEP_SCAN_COMMENTS:1':
        isUniq = message.payload not in [i for i in Admin_panel_db.fetch_buttons(state.state)]

        if not isUniq:
            await message.answer(f"Нельзя выбрать одну группу несколько раз")
        else:
            await message.answer(f"Вы выбрали группу {message.text}")
            Admin_panel_db.save_button(message.payload, state.state)
        return isUniq

    elif state.state == 'DEEP_SCAN_COMMENTS:2':
        isUniq = message.text not in [i for i in Admin_panel_db.fetch_values(state.state)]

        if not isUniq:
            await message.answer(f"Нельзя выбрать одно слово несколько раз")
        else:
            await message.answer(f"Вы выбрали слово {message.text}")
            Admin_panel_db.save_value(message.text, state.state)
        return isUniq

    elif state.state == 'DEEP_SCAN_COMMENTS:3':
        isUniq = message.payload not in [i for i in Admin_panel_db.fetch_values(state.state)]
        if not isUniq:
            await message.answer(f"Нельзя выбрать одного человека несколько раз")
        else:
            await message.answer(f"Вы выбрали человека {message.text}")
            print(message.payload)
            Admin_panel_db.save_value(message.payload, state.state)
        return isUniq
    else:
        raise('Ошибка клавиатуры')



@bp.on.message(lev="Глубокое сканирование комменты")
async def first_choice(message: Message):
    keyboard = Keyboard()
    keyboard.row()
    keyboard.add(Text('Поиск по словам'), KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text('Поиск по комментам людей'), KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text('Назад'), KeyboardButtonColor.PRIMARY)
    keyboard.get_json()
    await bp.state_dispenser.set(message.peer_id, DEEP_SCAN_COMMENTS.FIRST_CHOICE)
    await message.answer('Выберите поиск', keyboard=keyboard)

@bp.on.message(state=DEEP_SCAN_COMMENTS.FIRST_CHOICE)
async def make_choice(message: Message):
    if message.text == 'Поиск по словам':
        await choose_item(message)
    elif message.text == 'Поиск по комментам людей':
        await choose_item(message, scan_on_people=True)
    elif message.text == 'Назад':
        await bp.state_dispenser.delete(message.peer_id)
        await comments_finished(message)
    else:
        return 'Неправильный выбор'


async def choose_item(message: Message, scan_on_people=None):

    state = await bp.state_dispenser.get(message.peer_id)

    if state.state != 'DEEP_SCAN_COMMENTS:1':
        print('Not State')
        page_number = 0
        Admin_panel_db.clear_buffer()
        await bp.state_dispenser.set(message.peer_id, DEEP_SCAN_COMMENTS.CHOOSE_GROUP)
    else:
        page_number = Admin_panel_db.fetch_page_number()



    all_groups = Admin_panel_db.fetch_all_groups()
    buttons = all_groups[0 + (page_number * 6): ((page_number + 1) * 6)]


    keyboard = Keyboard()
    for count, button in enumerate(buttons):
        filtered = await bp.api.groups.get_by_id(group_id=button)
        if count == 0:
            keyboard.row()
            keyboard.add(Text(f'{filtered[0].name}', f'{button}'))
        elif count % 2 == 0:
            keyboard.row()
            keyboard.add(Text(f'{filtered[0].name}', f'{button}'))
        else:
            keyboard.add(Text(f'{filtered[0].name}', f'{button}'))

    keyboard.row()
    keyboard.add(Text('Назад'), KeyboardButtonColor.PRIMARY)
    keyboard.add(Text('Вперёд'), KeyboardButtonColor.PRIMARY)
    keyboard.row()
    if not scan_on_people:
        keyboard.add(Text('Окончить выбор', '986756493875334'), KeyboardButtonColor.POSITIVE)
    elif scan_on_people:
        keyboard.add(Text('Окончить выбор', '986756493875335'), KeyboardButtonColor.POSITIVE)
    keyboard.get_json()


    await message.answer(
        message="Выберите группу",
        keyboard=keyboard)



@bp.on.message(state=DEEP_SCAN_COMMENTS.CHOOSE_WORD)
async def choose_word(message: Message):

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

    keyboard.get_json()  # Эта кнопка ведёт обратно в deep_scaning_comments

    await message.answer(
        message="Выберите слова",
        keyboard=keyboard)

@bp.on.message(state=DEEP_SCAN_COMMENTS.CHOOSE_USERS_IDS)
async def choose_user_ids(message: Message):
    page_number = Admin_panel_db.fetch_page_number()
    all_usrs_ids = Admin_panel_db.fetch_all_users_ids()
    buttons = all_usrs_ids[0 + (page_number * 6): ((page_number + 1) * 6)]

    keyboard = Keyboard()
    for count, button in enumerate(buttons):
        filtered = await bp.api.users.get(user_ids=button)
        if count == 0:

            keyboard.row()
            keyboard.add(Text(f'{filtered[0].first_name}', f"{button}"))

        elif count % 2 == 0:
            keyboard.row()
            keyboard.add(Text(f'{filtered[0].first_name}', f"{button}"))
        else:
            keyboard.add(Text(f'{filtered[0].first_name}', f"{button}"))

    keyboard.row()
    keyboard.add(Text('Назад'), KeyboardButtonColor.PRIMARY)
    keyboard.add(Text('Вперёд'), KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text('Окончить выбор', payload='9584756385938524'), KeyboardButtonColor.POSITIVE)
    keyboard.get_json()

    await message.answer(message="Выберите человека", keyboard=keyboard)




@bp.on.message(state=DEEP_SCAN_COMMENTS.LOAD_CHOICE)
async def comments_preloading(message: Message, scan_on_people=None):



    result_groups_chosen = Admin_panel_db.fetch_buttons('DEEP_SCAN_COMMENTS:1')


    result_groups = ''
    for i in result_groups_chosen:
        filtered = await bp.api.groups.get_by_id(group_id=i)
        result_groups += f'{filtered[0].name} \n'


    if not scan_on_people:
        kb = Keyboard()
        kb.add(Text('Начать сканирование', payload='1'), KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text('Завершить досрочно'), KeyboardButtonColor.NEGATIVE)
        result_words = ''
        result_value_chosen = Admin_panel_db.fetch_values('DEEP_SCAN_COMMENTS:2')
        for i in result_value_chosen:
            result_words += f'\n{i} '
        await bp.api.messages.send(message=f'Выбраны слова: {result_words}\n \nИ группы:\n {result_groups}',
                                   peer_id=message.peer_id,
                                   random_id=random.randrange(100000000000000000000000), keyboard=kb.get_json())
        await bp.state_dispenser.set(message.peer_id, DEEP_SCAN_COMMENTS.DEEP_WAITING)

    elif scan_on_people:
        kb = Keyboard()
        kb.add(Text('Начать сканирование', payload='2'), KeyboardButtonColor.PRIMARY)
        kb.row()
        kb.add(Text('Завершить досрочно'), KeyboardButtonColor.NEGATIVE)
        result_users = ''
        result_value_chosen = Admin_panel_db.fetch_values(script_part='DEEP_SCAN_COMMENTS:3')

        for i in result_value_chosen:
            user_name = await bp.api.users.get(user_id=i)

            result_users += f'\n{user_name[0].first_name} {user_name[0].last_name}'
        await bp.api.messages.send(message=f'Выбраны люди: {result_users}\n И группы:\n {result_groups}',
                                   peer_id=message.peer_id,
                                   random_id=random.randrange(100000000000000000000000), keyboard=kb.get_json())
        await bp.state_dispenser.set(message.peer_id, DEEP_SCAN_COMMENTS.DEEP_WAITING)

    else:
        raise('Ошибка клавиатуры')


@bp.on.message(state=DEEP_SCAN_COMMENTS.DEEP_WAITING)
async def comments_loading(message: Message):
    global thread

    group_ids = Admin_panel_db.fetch_buttons(script_part='DEEP_SCAN_COMMENTS:1')

    if group_ids:
        if message.text == 'Завершить досрочно':
            await bp.state_dispenser.delete(message.peer_id)
            await comments_finished(message)
            Admin_panel_db.clear_buffer()

        elif message.text == 'Начать сканирование':
            if message.payload == '1':
                CommentsDownloader = Comments_finder()
                searched_items = Admin_panel_db.fetch_values(script_part='DEEP_SCAN_COMMENTS:2')

            elif message.payload == '2':
                CommentsDownloader = Comments_finder_on_people()
                searched_items = Admin_panel_db.fetch_values(script_part='DEEP_SCAN_COMMENTS:3')

            print(searched_items, group_ids)
            thread = threading.Thread(target=CommentsDownloader.go_search,
                                              args=(message.peer_id, [i for i in searched_items],
                                                    [f'-{i}' for i in group_ids]))

            allow_parsing_thread()
            thread.start()
            await message.answer('Началась загрузки. В зависимости от выбранных групп загрузка может быть очень долгой,'
                                 'вплоть до 4-5 часов.')
            Admin_panel_db.clear_buffer()

    else:
        if message.text == 'Завершить досрочно':
            await message.answer('Сканирование отменено')
            stop_parsing_thread()
            thread.join()
            await bp.state_dispenser.delete(message.peer_id)
            await comments_finished(message)

        else:
            await message.answer('Чтобы прервать сканирование, нажмите "Завершить досрочно"')



async def comments_finished(message: Message):

    await message.answer('Опять работа?', keyboard=start_keyboard)