from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    ATTR_NAME           = 0
    ATTR_VALUE          = 1
    ATTR_RELATION       = 2
    ATTR_AND            = 3
    TOKEN_QUANTIFIER    = 4
    TOKEN_LABEL         = 5
    EMPTY_TOKEN         = 6
    DEFAULT_TOKEN       = 7
    LPAREN              = 8
    RPAREN              = 9

@dataclass
class Token:
    type: TokenType
    value: any = None
    
    def __repr__(self):
        return self.type.name + (f":{self.value}" if self.value is not None else "")


