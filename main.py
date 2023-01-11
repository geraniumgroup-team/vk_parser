from config import log_parser, public_token
from vkbottle import load_blueprints_from_package
from vkbottle.bot import Message, Bot
from models import *
from loguru import logger
from STATES import START_PANEL_STATES
from vkbottle import Keyboard, KeyboardButtonColor, Text
from start_keyboard import start_keyboard
from admin_manager import Adding_admin_data, User, Group, Word

logger.remove()
colored_tales = public_token
logging = log_parser()
bot = Bot(token=colored_tales)
Admin_panel_db = Admin_panel_db()
Adding_admin_data = Adding_admin_data(bot)

print(10)


@bot.on.message(lev="Начать")
async def start_work(message: Message):
    keyboard = Keyboard()
    keyboard.add(Text('Продолжить'), KeyboardButtonColor.PRIMARY)
    await message.answer('Внимание! Данным ботом можно пользоваться только с одной страницы единовременно.'
                         'При использовании с двух страциц и более бот будет отвечать только одной, сбоить и вылетать', keyboard=keyboard)
    await bot.state_dispenser.set(message.peer_id, START_PANEL_STATES.START_STATE)
    from vk_parser import set_admin_id
    set_admin_id(123)
    for bp in load_blueprints_from_package("blueprints"):
        bp.load(bot)


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


bot.run_forever()

