from vkbottle.bot import Blueprint
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle import BaseStateGroup, GroupEventType, GroupTypes, StatePeer
from models import Admin_panel_db
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from start_keyboard import start_keyboard
from vk_parser.Deep_likes_finder import Deep_likes
from vk_parser import stop_parsing_thread, allow_parsing_thread
import threading

Admin_panel_db = Admin_panel_db()
bp = Blueprint("for chat commands")

class MyRule(ABCRule[Message]):
    async def check(self, message: Message) -> bool:
        state = await bp.state_dispenser.get(message.peer_id)

        if isinstance(state, StatePeer):
            if state.state == 'DEEP_LIKES:0':
                return True
            else:
                return False

class DEEP_LIKES(BaseStateGroup):
      CHOOSE_GROUP = 0
      CHOOSE_USER= 2
      DEEP_WAITING = 3

@bp.on.message(MyRule())
async def handle_callback_event(message: Message):
    page_number = Admin_panel_db.fetch_page_number()
    state = await bp.state_dispenser.get(message.peer_id)

    if message.text == 'Вперёд':
        page_number += 1
        Admin_panel_db.set_page_number(page_number)
        if page_number > 0:
            if state.state == 'DEEP_LIKES:0':
                await choose_item(message)

    elif message.text == 'Назад':
        page_number -= 1
        Admin_panel_db.set_page_number(page_number)
        if page_number >= 0:
            await choose_item(message)
        else:
            await bp.state_dispenser.delete(message.peer_id)
            Admin_panel_db.set_page_number(0)
            await likes_finished(message)


    elif message.text == 'Окончить выбор':
        Admin_panel_db.set_page_number(0)
        await message.answer(
            message="Введите id пользователя (только числовое значение)", keyboard=Keyboard().get_json())

        await bp.state_dispenser.set(message.peer_id, DEEP_LIKES.CHOOSE_USER)
        await chose_user_id(message)

    else:
        await is_button_clicked(message)



async def is_button_clicked(message: Message):

    state = await bp.state_dispenser.get(message.peer_id)
    isUniq = message.payload not in [i for i in Admin_panel_db.fetch_buttons(state.state)]

    if not isUniq:
        await message.answer(f"Нельзя выбрать одну группу несколько раз")

    else:
        await message.answer(f"Вы выбрали группу {message.text}")
        Admin_panel_db.save_button(message.payload, 'DEEP_LIKES:0')

@bp.on.message(lev='Глубокое сканирование лайки')
async def choose_item(message: Message):

    state = await bp.state_dispenser.get(message.peer_id)

    if not state:
        page_number = 0
        Admin_panel_db.clear_buffer()
        await bp.state_dispenser.set(message.peer_id, DEEP_LIKES.CHOOSE_GROUP)
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
    keyboard.add(Text('Окончить выбор', '986756493875334'), KeyboardButtonColor.POSITIVE)
    keyboard.get_json()

    await message.answer(
        message="Выберите группу",
        keyboard=keyboard)


@bp.on.message(state=DEEP_LIKES.CHOOSE_USER)
async def chose_user_id(message: Message):

    start_menu_buttons = ['Добавить слова', 'Удалить слова',
                          'Добавить группы', 'Удалить группы','Глубокое сканирование лайки',
                          'Глубокое сканирование комменты']

    if message.text.isdigit():
        username = await bp.api.users.get([message.text])

        if message.text in start_menu_buttons:
            await bp.state_dispenser.delete(message.peer_id)
            Admin_panel_db.clear_buffer()
        if username and  username[0].first_name != 'DELETED' and len(message.text)<=30:

           Admin_panel_db.save_value(message.text, 'DEEP_LIKES:0')
           await bp.state_dispenser.set(message.peer_id, DEEP_LIKES.DEEP_WAITING)

           kb = Keyboard()
           kb.add(Text('Начать сканирование'), KeyboardButtonColor.PRIMARY)
           kb.row()
           kb.add( Text('Завершить досрочно'), KeyboardButtonColor.NEGATIVE)

           await message.answer(f'Выбран пользователь {username[0].first_name} {username[0].last_name}. Время сканирования может быть длинным.',
                          keyboard=kb)

        else:
            return'Пользователь не существует или удалён'
    else:
        return 'В id есть что-то, кроме цифр или id неверный'


@bp.on.message(state=DEEP_LIKES.DEEP_WAITING)
async def likes_loading(message: Message):
    global thread

    group_ids = Admin_panel_db.fetch_buttons(script_part='DEEP_LIKES:0')
    serched_id = Admin_panel_db.fetch_values(script_part='DEEP_LIKES:0')
    Admin_panel_db.clear_buffer()

    print(serched_id)
    if group_ids:
        thread = threading.Thread(target=Deep_likes().send_result,
                                          args=([f'-{i}' for i in group_ids], message.peer_id,
                                                int(serched_id[0])))
        if message.text == 'Завершить досрочно':
            await message.answer('Сканирование отменено')
            await bp.state_dispenser.delete(message.peer_id)
            await likes_finished(message)

        elif message.text == 'Начать сканирование':
            allow_parsing_thread()
            thread.start()

            await message.answer(
                'Началась загрузки. В зависимости от выбранных групп загрузка может быть очень долгой,'
                'вплоть до 4-5 часов.')

    else:
        if message.text == 'Завершить досрочно':
            stop_parsing_thread()
            await message.answer('Сканирование отменено')
            await bp.state_dispenser.delete(message.peer_id)
            await likes_finished(message)

        else:
            await message.answer('Чтобы прервать сканирование, нажмите "Завершить досрочно"')



async def likes_finished(message: Message):

    await message.answer('Опять работа?', keyboard=start_keyboard)

