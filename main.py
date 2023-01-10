from config import log_parser, public_token
from vkbottle import load_blueprints_from_package
from vkbottle.bot import Message, Bot
from models import *
from loguru import logger
from STATES import START_PANEL_STATES
from vkbottle import Keyboard, KeyboardButtonColor, Text
from start_keyboard import start_keyboard

logger.remove()
colored_tales = public_token
logging = log_parser()
bot = Bot(token=colored_tales)
Admin_panel_db = Admin_panel_db()

for bp in load_blueprints_from_package("blueprints"):
    bp.load(bot)

@bot.on.message(lev="Начать")
async def start_work(message: Message):
    keyboard = Keyboard()
    keyboard.add(Text('Продолжить'), KeyboardButtonColor.PRIMARY)
    await message.answer('Внимание! Данным ботом можно пользоваться только с одной страницы единовременно.'
                         'При использовании с двух страциц и более бот будет отвечать только одной, сбоить и вылетать', keyboard=keyboard)
    await bot.state_dispenser.set(message.peer_id, START_PANEL_STATES.START_STATE)

@bot.on.message(state=START_PANEL_STATES.START_STATE)
async def start_handler(message: Message):

    await message.answer('Опять работать?', keyboard=start_keyboard)
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.message(lev="Добавить группы")
async def reg_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, START_PANEL_STATES.INSTERT_GROUP)
    await message.answer('Введите id группы(в числовом формате), без дефиса вначале. Чтобы узнать id группы, '
                         'откройте любую фотографию на стене или в альбомах групы и откройте URL-адрес над'
                         'фотографией. Дальше ищите по шаблону:'
                         ' https://vk.com/НАЗВАНИЕ_ГРУППЫ?z=photo-ЗДЕСЬ БУДЕТ ID_457580757%2Fwall-ЗДЕСЬ ТОЖЕ БУДЕТ ID_11421978')


@bot.on.message(state=START_PANEL_STATES.INSTERT_GROUP)
async def name_handler(message: Message):
    print('INSTERT_GROUP')
    if message.text.isdigit():
        group_name = await bot.api.groups.get_by_id(message.text)
        groups = Admin_panel_db.getGroupIds()

        if int(message.text) in [group for group in groups]:
            await message.answer(f'Группа {group_name[0].name} уже была добавлена ранее')

        elif int(message.text) not in [group for group in groups] and len(message.text) < 20:

            new_word = Group_ids(group_id=message.text)
            session.add(new_word)
            session.commit()
            await message.answer(f'Группа {group_name[0].name} добавлена. '
                                 f'Чтобы добавить новую группу, нажмите на кнопку ещё раз.')
    else:
        await message.answer(f'Id группы введено в неправильном формате')
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.message(lev="Добавить слова")
async def reg_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, START_PANEL_STATES.INSERT_WORD)
    await message.answer('Введите слово или фразу')


@bot.on.message(state=START_PANEL_STATES.INSERT_WORD)
async def name_handler(message: Message):

    words = session.query(Words).all()
    await bot.state_dispenser.delete(message.peer_id)

    if message.text in [word.word for word in words]:
        await message.answer(f'Слово {message.text} уже есть в списке слов.')

    elif message.text not in words and len(message.text) < 20:
        session.add(Words(word=message.text))
        session.commit()

        await message.answer(f'Слово {message.text} добавлено. Чтобы добавить новое слово, нажмите на '
                             f'кнопку ещё раз')

    else:
        await message.answer(f'Вероятно, слово или фраза слищком длинные. Максимальная длина - 20 символов с пробелами.')

@bot.on.message(lev="Добавить людей")
async def reg_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, START_PANEL_STATES.INSERT_USER)
    kb = Keyboard()
    kb.add(Text('Завершить'), KeyboardButtonColor.NEGATIVE)
    kb.row()
    kb.add(Text('Какие пользователи есть в базе?'), KeyboardButtonColor.POSITIVE)
    await message.answer('Введите id человека', keyboard=kb.get_json())


@bot.on.message(state=START_PANEL_STATES.INSERT_USER)
async def name_handler(message: Message):
    users = Admin_panel_db.fetch_all_users_ids()

    if message.text == 'Завершить':
        await bp.state_dispenser.delete(message.peer_id)
        await start_handler(message)

    elif message.text == 'Какие пользователи есть в базе?':

        if users:
            text = ''
            for count, user_id in enumerate(users):
                username = await bp.api.users.get(user_id)
                text += f'**{count+1}.{username[0].first_name} {username[0].last_name} Id:{user_id}** \n'
            await message.answer(text)

        else:
            await message.answer('В базе нет пользователей')

    else:
        if message.text.isdigit():
            username = await bp.api.users.get([message.text])


            if username and username[0].first_name != 'DELETED' and len(message.text) <= 15:
                if int(message.text) in users:
                    return 'Этот пользователь уже существует в приложении'
                else:
                    Admin_panel_db.add_user_id(message.text)
                    await message.answer(
                        f'Добавлен пользователь {username[0].first_name} {username[0].last_name}')
            else:
                return 'Пользователь не существует или удалён'
        else:
            return 'В id есть что-то, кроме цифр'

bot.run_forever()

