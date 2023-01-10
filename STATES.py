from vkbottle import BaseStateGroup

class START_PANEL_STATES(BaseStateGroup):
    START_STATE = 0
    INSTERT_GROUP = 1
    INSERT_WORD = 2
    INSERT_USER = 3
    CHOOSE_WORD = 4

class BACKGROUND_COMMENTS(BaseStateGroup):
    CHOOSE_GROUP = 0
    CHOOSE_WORD = 1
    LOAD_CHOICE = 2
    WAITING_FOR_START = 3
    DEEP_WAITING = 4

class DELETE_WORD_STATES(BaseStateGroup):
    CHOOSE_WORD = 1


class DEEP_SCAN_COMMENTS(BaseStateGroup):
    FIRST_CHOICE = 0
    CHOOSE_GROUP = 1
    CHOOSE_WORD = 2
    CHOOSE_USERS_IDS = 3
    LOAD_CHOICE = 4
    DEEP_WAITING = 5

class COMMON_STATES(BaseStateGroup):
    CHOOSE_GROUP = 1
    CHOOSE_USER_ID = 1