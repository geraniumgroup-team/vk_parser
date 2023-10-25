from .typing.exception_types import *
from typing.objects import CodeExceptions
from abc import abstractmethod, ABC

class BaseHandler(ABC):

    @abstractmethod
    def log_error(self):
        pass

    
