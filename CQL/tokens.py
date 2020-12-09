from enum import Enum

class TokenType(Enum):
    ATTR_NAME           = 0
    ATTR_VALUE          = 1
    ATTR_RELATION       = 2
    ATTR_AND            = 3
    TOKEN_QUANTIFIER    = 4
    TOKEN_LABEL         = 5
    SEP                 = 6
    EMPTY_TOKEN         = 7
    DEFAULT_TOKEN       = 8


class Token:
    def __init__(self, type_:TokenType, value:any=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return self.type.name + (f":{self.value}" if self.value is not None else "")


