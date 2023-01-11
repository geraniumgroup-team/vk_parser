from vk_parser.auth_vk import *
from .exceptions import exception_handler
stop_parsing = False

vk = auth()
vk_session_group = vk_session_group

def show_parsing_state():
    global stop_parsing
    return stop_parsing

def stop_parsing_thread():
    global stop_parsing
    stop_parsing = True

def allow_parsing_thread():
    global stop_parsing
    stop_parsing = False