from tokens import TokenType
from nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.advance()

    def raise_error(self):
        raise Exception("Syntax Error")

    def advance(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None

    def parse(self):
        if self.current_token is None:
            return None

        result = self.list_wordGroups()

        if self.current_token != None:
            self.raise_error()

        return result

    def list_wordGroups(self):
        result = []
        while self.current_token != None:
            group = self.wordGroup()
            result.append(group)

        return result

    def wordGroup(self):
        token = self.current_token
        word_group = []
        label = None
        quant = None

        # Check whether group is labeled
        if token.type == TokenType.TOKEN_LABEL:
            label = token.value
            self.advance()

        # Parentheses as group
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            while self.current_token != None and self.current_token.type in {TokenType.DEFAULT_TOKEN, TokenType.EMPTY_TOKEN, TokenType.TOKEN_LABEL, TokenType.ATTR_NAME, TokenType.LPAREN, TokenType.TOKEN_LABEL}:
                if self.current_token.type == TokenType.LPAREN:
                    result = self.wordGroup()
                elif self.current_token.type == TokenType.TOKEN_LABEL:
                    result = self.wordGroup()
                else:
                    result = self.word()
                    #print(f"  {result}")
                    #print(f"  {self.current_token}")
                word_group.append(result)
            
            if self.current_token.type != TokenType.RPAREN:
                self.raise_error()
            self.advance()

            # Check trailing quantifier
            if self.current_token != None and self.current_token.type == TokenType.TOKEN_QUANTIFIER:
                quant = self.current_token.value
                self.advance()

            # Add label and quantifiers to group
            if quant != None:
                word_group = QuantifyNode(word_group, quant)
            if label != None:
                word_group = LabelNode(word_group, label)

            return word_group

        # Single word
        elif self.current_token.type in {TokenType.DEFAULT_TOKEN, TokenType.EMPTY_TOKEN, TokenType.ATTR_NAME}:
            #print(self.current_token)
            word_group = self.word()
            #print(word_group)
            if label != None:
                word_group = LabelNode(word_group, label)

            return word_group


    def word(self):
        quant = None
        # Directly return DEFAULT/EMPTY_TOKEN
        if self.current_token.type in {TokenType.DEFAULT_TOKEN, TokenType.EMPTY_TOKEN}:
            if self.current_token.type == TokenType.DEFAULT_TOKEN:
                word = DefaultTokenNode(self.current_token.value)
            else:
                word = EmptyTokenNode()

            # Check trailing quantifier
            self.advance()
            if self.current_token != None and self.current_token.type == TokenType.TOKEN_QUANTIFIER:
                quant = self.current_token.value
                self.advance()

            if quant != None:
                word = QuantifyNode(word, quant)

            return word

        # Construct word from attributes
        word = self.word_attrpair()

        while self.current_token != None and self.current_token.type == TokenType.ATTR_AND:
            self.advance()
            word = ConjoinAttrNode(word, self.word_attrpair())

        # Check quantifier
        if self.current_token != None and self.current_token.type == TokenType.TOKEN_QUANTIFIER:
            quant = self.current_token.value
            self.advance()
        if quant != None:
            word = QuantifyNode(word, quant)

        return word


    def word_attrpair(self):
        token = self.current_token

        if token.type == TokenType.ATTR_NAME:
            self.advance()
            if self.current_token.type == TokenType.ATTR_RELATION:
                operator = self.current_token.value
                self.advance()
                if self.current_token.type == TokenType.ATTR_VALUE:
                    result = AssignAttrNode(
                        AttrNameNode(token.value),
                        operator,
                        AttrValueNode(self.current_token.value))
                    self.advance()
                    return result

        self.raise_error()
