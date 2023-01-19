from vk_parser.auth_vk import *
from .exceptions import exception_handler
import os
stop_parsing = False

admin_id = int(os.environ["admin_id"])
vk = auth(admin_id)
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