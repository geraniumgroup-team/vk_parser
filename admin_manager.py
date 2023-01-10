from typing import Union, Optional
from vkbottle import KeyboardButtonColor, Text, Bot, BotBlueprint, Keyboard
from vkbottle.bot import Blueprint, Message
from models import session, Group_ids, Words, Admin_panel_db
from start_keyboard import start_keyboard

Admin_panel_db = Admin_panel_db()
class Word():
    def __init__(self, text: Union[int, str, None] = None):
        self.text = text

    def __str__(self):
        return self.text

    adding_button = Text('Какие слова есть в базе?'), KeyboardButtonColor.POSITIVE

class User():
    def __init__(self, bot: Union[Bot, BotBlueprint] = None, user_id: Optional[int] = None):
        self.user_id = user_id
        self.bot = bot


    @property
    async def username(self):
        username = await self.bot.api.users.get([self.user_id])
        return username

    @property
    async def first_name(self):
        name = await self.username
        return name[0].first_name

    @property
    async def last_name(self):
        name = await self.username
        return name[0].last_name

    adding_button = Text('Какие пользователи есть в базе?'), KeyboardButtonColor.POSITIVE


class Group():
    def __init__(self, bot: Union[Bot, BotBlueprint, None] = None, group_id: Union[int, str] = None):
        self.group_id = group_id
        self.bot = bot

    @property
    async def group_name(self):
        group_name = await self.bot.api.groups.get_by_id([self.group_id])
        return group_name[0].name

    adding_button = Text('Какие группы есть в базе?'), KeyboardButtonColor.POSITIVE


class Adding_admin_data():

    def __init__(self, bot: Union[Bot, BotBlueprint]):
        self.bot = bot
    async def add_keyboard(self, message: Message, keyboard: Keyboard, button: Union[Word, User, Group]):
        keyboard.add(Text('Завершить'), KeyboardButtonColor.NEGATIVE)
        keyboard.row()
        keyboard.add(*button.adding_button)
        hint = {Word: 'Введите слово или фразу.',
                    User: 'Введите id человека (в числовом формате).',
                    Group: 'Введите id группы (в числовом формате), без дефиса вначале.'}

        await message.answer(hint[type(button)], keyboard=keyboard.get_json())

    async def set_conditions(self, message: Message, adding_item: Union[Word, User, Group]):
        if message.text == 'Завершить':
            await self.bot.state_dispenser.delete(message.peer_id)
            await message.answer('Опять работать?', keyboard=start_keyboard)

        if isinstance(adding_item, User):
            users = Admin_panel_db.fetch_all_users_ids()
            if message.text == 'Какие пользователи есть в базе?':
                if users:
                    text = ''
                    for count, user_id in enumerate(users):
                        user = User(self.bot, user_id)
                        text += f'**{count + 1}.{await user.first_name} {await user.last_name} Id:{user.user_id}** \n'
                    await message.answer(text)
                else:
                    await message.answer('В базе нет пользователей')
            else:
                if message.text.isdigit():
                    user = User(self.bot, message.text)

                    if await user.first_name and await user.first_name != 'DELETED' and len(message.text) <= 15:
                        if int(user.user_id) in users:
                            await message.answer('Этот пользователь уже существует в приложении')
                        else:
                            Admin_panel_db.add_user_id(user.user_id)
                            await message.answer(
                                f'Добавлен пользователь {await user.first_name} {await user.last_name}')
                    else:
                        await message.answer('Пользователь не существует или удалён')
                else:
                    await message.answer('В id есть что-то, кроме цифр')


        elif isinstance(adding_item, Word):
            existing_words = session.query(Words).all()
            word = Word(message.text)
            if message.text == 'Какие слова есть в базе?':

                if existing_words:
                    text = ''
                    for existing_word in existing_words:
                        text += f'**{existing_word.word}**, '
                    await message.answer(text)

                else:
                    await message.answer('В базе нет слов')

            else:

                if str(word) in [existing_word.word for existing_word in existing_words]:
                    await message.answer(f'Слово {word} уже есть в списке слов.')
                elif message.text not in existing_words and len(message.text) < 20:
                    session.add(Words(word=str(word)))
                    session.commit()

                    await message.answer(f'Слово {word} добавлено.')
                else:
                    await message.answer(f'Вероятно, слово или фраза слищком длинные. Максимальная длина - 20'
                                         f' символов с пробелами.')

        elif isinstance(adding_item, Group):
            groups = Admin_panel_db.getGroupIds()
            if message.text == 'Какие группы есть в базе?':
                if groups:
                    text = ''
                    for count, group_id in enumerate(groups):
                        group = Group(self.bot, group_id)
                        text += f'**{count + 1}.{await group.group_name} ++ Id:{group.group_id}** \n'
                    await message.answer(text)
                else:
                    await message.answer('В базе нет групп')

            elif message.text.isdigit():

                group = Group(self.bot, int(message.text))

                print(type(group.group_id), [existing_group for existing_group in groups])
                if group.group_id in [existing_group for existing_group in groups]:
                    print(group.group_id, [existing_group for existing_group in groups])
                    await message.answer(f'Группа {await group.group_name} уже была добавлена ранее')

                elif int(message.text) not in [group for group in groups] and len(message.text) < 20:

                    new_word = Group_ids(group_id=message.text)
                    session.add(new_word)
                    session.commit()
                    await message.answer(f'Группа {await group.group_name} добавлена.')
            else:
                await message.answer(f'Id группы введено в неправильном формате')
