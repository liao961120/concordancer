from tokens import Token, TokenType

WHITESPACE = ' \t\n'
ESCAPECHAR = '\\'
NAME_CHARS = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-.')
DIGITS = set('0123456789')
QUANTIFIERS = set('?+*')

class Lexer:
    def __init__(self, text):
        self.text = iter(text.strip())
        self.current_char = None
        self.char_in_token_brackets = False
        self.char_in_attr_quotes = False
        self.char_in_quantifiers = False
        self.advance()
    
    def advance(self):
        try:
            self.current_char = next(self.text)
        except StopIteration:
            self.current_char = None
    
    def generate_tokens(self):
        while self.current_char is not None:
            # TOKEN open quote
            if (not self.char_in_token_brackets) and self.current_char == '[':
                self.char_in_token_brackets = True
                self.advance()
            # TOKEN closing quote
            elif self.char_in_token_brackets and self.current_char == ']':
                self.char_in_token_brackets = False
                self.advance()
            # ATTR_VALUE open quote
            elif (not self.char_in_attr_quotes) and self.current_char == '"':
                self.char_in_attr_quotes = True
                self.advance()
            # ATTR_VALUE closing quote
            elif self.char_in_attr_quotes and self.current_char == '"':
                self.char_in_attr_quotes = False
                self.advance()
            # Escapes in ATTR_VALUE
            elif self.char_in_attr_quotes and self.current_char == ESCAPECHAR:
                self.advance()
                self.advance()
            # ATTR_RELATION
            elif self.char_in_token_brackets and (not self.char_in_attr_quotes) and (self.current_char == '!' or self.current_char == '='):
                yield self.generate_attr_relation()
            # ATTR_NAME
            elif self.char_in_token_brackets and (not self.char_in_attr_quotes) and self.current_char in NAME_CHARS:
                yield self.generate_attr_name()
            # ATTR_VALUE
            elif self.char_in_token_brackets and self.char_in_attr_quotes and self.current_char in NAME_CHARS:
                yield self.generate_attr_value()
            # Spaces between ATTR
            elif self.char_in_token_brackets and (not self.char_in_attr_quotes) and self.current_char in WHITESPACE:
                self.advance()
            # ATTR_AND
            elif self.char_in_token_brackets and (not self.char_in_attr_quotes) and self.current_char == '&':
                yield Token(TokenType.ATTR_AND)
                self.advance()
            # SEP
            elif (not self.char_in_token_brackets) and self.current_char in WHITESPACE:
                yield self.generate_separator()
            # TOKEN_LABEL
            elif (not self.char_in_token_brackets) and (not self.char_in_attr_quotes) and self.current_char in NAME_CHARS:
                yield self.generate_token_label()
            # TOKEN_LABEL end
            elif (not self.char_in_token_brackets) and (not self.char_in_attr_quotes) and self.current_char == ':':
                self.advance()
            # TOKEN_QUANTIFIER open quote
            elif (not self.char_in_token_brackets) and (not self.char_in_attr_quotes) and (not self.char_in_quantifiers) and self.current_char == '{':
                self.char_in_quantifiers = True
                self.advance()
            # TOKEN_QUANTIFIER closing quote
            elif (not self.char_in_token_brackets) and (not self.char_in_attr_quotes) and self.char_in_quantifiers and self.current_char == '}':
                self.char_in_quantifiers = False
                self.advance()
            # TOKEN_QUANTIFIER
            elif self.char_in_quantifiers and self.current_char in DIGITS:
                self.generate_token_quantifier()
            elif (not self.char_in_token_brackets) and (not self.char_in_attr_quotes) and self.current_char in QUANTIFIERS:
                if self.current_char == '?':
                    yield Token(TokenType.TOKEN_QUANTIFIER, (0, 1))
                elif self.current_char == '+':
                    yield Token(TokenType.TOKEN_QUANTIFIER, (1, 'inf'))
                elif self.current_char == '*':
                    yield Token(TokenType.TOKEN_QUANTIFIER, (0, 'inf'))
                else:
                    raise Exception(f"Invalid character {self.current_char}")
                self.advance()
            else:
                raise Exception(f"Illegal character '{self.current_char}'")


    def generate_separator(self):
        while self.current_char is not None and self.current_char in WHITESPACE:
            self.advance()
        return Token(TokenType.SEP)


    def generate_attr_name(self):
        name_str = self.current_char
        self.advance()

        while self.current_char != None and self.current_char in NAME_CHARS:
            name_str += self.current_char
            self.advance()

        return Token(TokenType.ATTR_NAME, name_str)


    def generate_attr_value(self):
        attr_str = self.current_char
        self.advance()

        while self.current_char != None and self.current_char != '"':
            if self.current_char == ESCAPECHAR:
                attr_str += self.current_char
                self.advance()
            
            attr_str += self.current_char
            self.advance()
        
        return Token(TokenType.ATTR_NAME, attr_str)

    def generate_attr_relation(self):
        if self.current_char == '=':
            return Token(TokenType.ATTR_RELATION, 'is')
        elif self.current_char == '!':
            self.advance()
            if self.current_char == '=':
                return Token(TokenType.ATTR_RELATION, 'is_not')
        raise Exception(f"Illegal character '{self.current_char}'")


    def generate_attr_and(self):
        pass

    def generate_token_quantifier(self):
        num_of_comma = 0
        q_min, q_max = None, None
        self.advance()

        while self.current_char != None and (self.current_char in DIGITS or self.current_char == ','):
            if self.current_char == ',':
                num_of_comma += 1
                if num_of_comma > 1: break
                self.advance()
            elif self.current_char in DIGITS:
                if q_min is None:
                    q_min = self.generate_int()
                else:
                    q_max = self.generate_int()
        
        if q_min is None or q_max is None:
            raise Exception(f"Invalid character in quantifier: {self.current_char}")

        return Token(TokenType.TOKEN_QUANTIFIER, (q_min, q_max))

    def generate_token_label(self):
        pass


    def generate_int(self):
        num_str = self.current_char
        self.advance()

        while self.current_char != None and self.current_char in DIGITS:
            num_str += self.current_char
            self.advance()
        
        return int(num_str)