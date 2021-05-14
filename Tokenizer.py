import re
import itertools


class Tokenizer:
    SPECIAL_CHARACTERS = {
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;'
    }
    LEXICAL_ELEMENTS_MATCHES = ['KEYWORD', 'SYMBOL', 'INT_CONST', 'STRING_CONST', 'IDENTIFIER']
    KEYWORD = '(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)(?=[^\w])'
    SYMBOL = '([{}()[\].,;+\-*/&|<>=~])'
    INT_CONST = '(\d+)'
    STRING_CONST = '\"([^\n]*)\"'
    IDENTIFIER = '([A-Za-z_]\w*)'
    LEXICAL_ELEMENTS = '{}|{}|{}|{}|{}'.format(KEYWORD, SYMBOL, INT_CONST, STRING_CONST, IDENTIFIER)
    LEXICAL_ELEMENTS_REGEX = re.compile(LEXICAL_ELEMENTS)
    INLINE_COMMENT_REGEX = re.compile('//.*\n')
    MULTILINE_COMMENT_REGEX = re.compile('/\*.*?\*/', flags=re.S)

    def __init__(self, input_file, token_file):
        self.input = input_file.read()
        self.tokens = self.tokenize()
        self.token_file = token_file
        self.tokens = list(self.tokens)
        self.next_token = self.tokens.pop(0)
        self.buffer = ''
        self.token_file.write('<tokens>\n')
        input_file.close()

    def has_more_tokens(self):
        return not not self.next_token

    def advance(self):
        self.current_token = self.next_token
        if len(self.tokens) != 0:
            self.next_token = self.tokens.pop(0)
            self.write_xml_token()
        else:
            self.write_xml_token()
            self.token_file.write('</tokens>\n')
            self.token_file.close()
            self.next_token = False

    def token_type(self):
        return self.current_token[1]

    def key_word(self):
        return self.current_token[0].upper()

    def symbol(self):
        return self.current_token[0]

    def identifier(self):
        return self.current_token[0]

    def int_val(self):
        return self.current_token[0]

    def string_val(self):
        return self.current_token[0]

    def write_xml_token(self):
        if self.token_type() is 'KEYWORD':
            self.token_file.write('<keyword> {} </keyword>\n'.format(self.key_word().lower))
        elif self.token_type() is 'SYMBOL':
            symbol = self.symbol()
            if symbol in self.SPECIAL_CHARACTERS.keys():
                symbol = self.SPECIAL_CHARACTERS[symbol]
            self.token_file.write('<symbol> {} </symbol>\n'.format(symbol))
        elif self.token_type() is 'IDENTIFIER':
            self.token_file.write('<identifier> {} </identifier>\n'.format(self.identifier()))
        elif self.token_type() is 'INT_CONST':
            self.token_file.write('<integerConstant> {} </integerConstant>\n'.format(self.int_val()))
        elif self.token_type() is 'STRING_CONST':
            self.token_file.write('<stringConstant> {} </stringConstant>\n'.format(self.string_val()))

    def tokenize(self):
        input_without_comments = self.remove_comments()
        matches = self.LEXICAL_ELEMENTS_REGEX.findall(input_without_comments)
        match_types = map(lambda element_matches: self.LEXICAL_ELEMENTS_MATCHES[
            next(index for index, element in enumerate(element_matches) if element)], matches)
        flat_matches = list(itertools.chain(*matches))
        tokens = [match for match in flat_matches if match]
        return zip(tokens, match_types)

    def remove_comments(self):
        without_multiline = re.sub(self.MULTILINE_COMMENT_REGEX, ' ', self.input)
        without_inline = re.sub(self.INLINE_COMMENT_REGEX, '\n', without_multiline)
        return without_inline