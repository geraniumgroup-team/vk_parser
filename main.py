from config import log_parser, public_token
from vkbottle import load_blueprints_from_package
from vkbottle.bot import Message, Bot
from models import *
from loguru import logger
from STATES import START_PANEL_STATES
from vkbottle import Keyboard, KeyboardButtonColor, Text
from start_keyboard import start_keyboard
from admin_manager import Adding_admin_data, User, Group, Word

logger.level("ERROR")
colored_tales = public_token
logging = log_parser()
bot = Bot(token=colored_tales)
Admin_panel_db = Admin_panel_db()
Adding_admin_data = Adding_admin_data(bot)

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
async def add_groups(message: Message):
    await Adding_admin_data.add_keyboard(message, Keyboard(), Group())
    await bot.state_dispenser.set(message.peer_id, START_PANEL_STATES.INSTERT_GROUP)


@bot.on.message(state=START_PANEL_STATES.INSTERT_GROUP)
async def insert_group_handler(message: Message):
    await Adding_admin_data.set_conditions(message, Group(bot, message.text))


@bot.on.message(lev="Добавить слова")
async def reg_handler(message: Message):
    await Adding_admin_data.add_keyboard(message, Keyboard(), Word())
    await bot.state_dispenser.set(message.peer_id, START_PANEL_STATES.INSERT_WORD)


@bot.on.message(state=START_PANEL_STATES.INSERT_WORD)
async def name_handler(message: Message):
    await Adding_admin_data.set_conditions(message, Word(message.text))


@bot.on.message(lev="Добавить людей")
async def reg_handler(message: Message):
    await Adding_admin_data.add_keyboard(message, Keyboard(), User())
    await bot.state_dispenser.set(message.peer_id, START_PANEL_STATES.INSERT_USER)


@bot.on.message(state=START_PANEL_STATES.INSERT_USER)
async def name_handler(message: Message):
    await Adding_admin_data.set_conditions(message, User(message.text))
    # users = Admin_panel_db.fetch_all_users_ids()
    #
    # if message.text == 'Завершить':
    #     await bp.state_dispenser.delete(message.peer_id)
    #     await start_handler(message)
    #
    # elif message.text == 'Какие пользователи есть в базе?':
    #
    #     if users:
    #         text = ''
    #         for count, user_id in enumerate(users):
    #             username = await bp.api.users.get(user_id)
    #             text += f'**{count+1}.{username[0].first_name} {username[0].last_name} Id:{user_id}** \n'
    #         await message.answer(text)
    #
    #     else:
    #         await message.answer('В базе нет пользователей')
    #
    # else:
    #     if message.text.isdigit():
    #         username = await bp.api.users.get([message.text])
    #
    #
    #         if username and username[0].first_name != 'DELETED' and len(message.text) <= 15:
    #             if int(message.text) in users:
    #                 return 'Этот пользователь уже существует в приложении'
    #             else:
    #                 Admin_panel_db.add_user_id(message.text)
    #                 await message.answer(
    #                     f'Добавлен пользователь {username[0].first_name} {username[0].last_name}')
    #         else:
    #             return 'Пользователь не существует или удалён'
    #     else:
    #         return 'В id есть что-то, кроме цифр'

bot.run_forever()

