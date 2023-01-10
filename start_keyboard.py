from vkbottle import Keyboard, KeyboardButtonColor, Text

start_keyboard = Keyboard()
start_keyboard.row()
start_keyboard.add(Text('Глубокое сканирование лайки'), KeyboardButtonColor.PRIMARY)
start_keyboard.row()
start_keyboard.add(Text('Глубокое сканирование комменты'), KeyboardButtonColor.PRIMARY)
start_keyboard.row()
start_keyboard.add(Text('Фоновое сканирование комментов'), KeyboardButtonColor.PRIMARY)
start_keyboard.row()
start_keyboard.add(Text('Добавить слова'), KeyboardButtonColor.PRIMARY)
start_keyboard.add(Text('Добавить группы'), KeyboardButtonColor.PRIMARY)

start_keyboard.row()
start_keyboard.add(Text('Удалить слова'), KeyboardButtonColor.PRIMARY)
start_keyboard.add(Text('Удалить группы'), KeyboardButtonColor.PRIMARY)
start_keyboard.row()
start_keyboard.add(Text('Добавить людей'), KeyboardButtonColor.PRIMARY)
start_keyboard.add(Text('Удалить людей'), KeyboardButtonColor.PRIMARY)
start_keyboard.row()
start_keyboard.add(Text('Перезагрузить бота'), KeyboardButtonColor.PRIMARY)

start_keyboard.get_json()
