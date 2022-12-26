"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

last_one = ''

keyword_list = ['class', 'constructor', 'function', 'method', 'field',
                'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                'false', 'null', 'this', 'let', 'do', 'if', 'else',
                'while', 'return']

keyWords = \
    {'boolean': 'BOOLEAN', 'char': 'CHAR', 'class': 'CLASS',
     'constructor': 'CONSTRUCTOR', 'do': 'DO', 'else': 'ELSE',
     'false': 'FALSE', 'field': 'FIELD', 'function': 'FUNCTION', 'if': 'IF',
     'int': 'INT', 'let': 'LET', 'method': 'METHOD', 'null': 'NULL',
     'return': 'RETURN', 'static': 'STATIC', 'this': 'THIS', 'true': 'TRUE',
     'var': 'VAR', 'void': 'VOID', 'while': 'WHILE'}

open_symbols = ['{', '(', '[', '<']
close_symbols = ['}', ')', ']', '>']
symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
               '-', '*', '/', '&', ',', '<', '>', '=', '~', '^', '#', '|']

temp2 = False
temp3 = False


# region helper function
def check_if_var_name(string: str) -> bool:
    if len(string) == 0:
        return False
    if string[0] == '"':
        string = string[1:]
    if len(string) == 0:
        return False
    if string[-1] == '"':
        string = string[:-1]

    # if string[0].isidentifier() and string.isalnum():
    #     return True
    # return False
    return string.isidentifier()


def is_constant_number(str) -> bool:
    if str.isnumeric():
        # Convert the string to an integer
        number = int(str)

        # Check if the number is in the range 0-32767
        if 0 <= number <= 32767:
            return True
        else:
            return False
    else:
        return False


# endregion


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x , y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true'
                |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.pos = 0
        self.file = []
        self.tokens = []
        input_lines = input_stream.read().splitlines()
        for line in input_lines:
            self.file.append(line)
        self.remove_slashes()
        self.remove_comments()
        self.remove_multy_comment()
        self.remove_comments()
        self.get_by_lines(input_stream)
        # self.tokens_type_list = []
        self.get_by_tokens()
        # self.connect_strings()

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.pos < len(self.tokens)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if it has_more_tokens() is true.
        Initially there is no current token.
        """
        if self.has_more_tokens():
            self.pos += 1

    def back(self):
        self.pos -= 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        current_token = self.get_token()
        if current_token in keyword_list:
            return "KEYWORD"
        elif current_token in symbol_list:
            return "SYMBOL"
        elif current_token[0] == '"' and current_token[-1] == '"':
            return "STRING_CONST"
        elif check_if_var_name(current_token):
            return "IDENTIFIER"
        elif is_constant_number(current_token):
            return "INT_CONST"

        else:
            raise TypeError(
                f"token_type function error token type unknown\n the input"
                f" was {self.get_token()}")

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.token_type() == "KEYWORD":
            return keyWords[self.get_token()]
        raise ValueError(
            f"keyword function wrong, the function get: {self.get_token()}")

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self.token_type() == "SYMBOL":
            return self.get_token()
        raise ValueError(
            f"symbol function wrong, the function get: {self.get_token()}")

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        if self.token_type() == "IDENTIFIER":
            return str(self.get_token())
        raise ValueError(
            f"identifier function wrong, the function get {self.get_token()}")

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        if self.token_type() == "INT_CONST":
            return int(self.get_token())
        raise ValueError(
            f"int_val function wrong, the function get {self.get_token()}")

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        if self.token_type() == "STRING_CONST":
            return self.get_token()[1:-1]
        raise ValueError(
            f"string_val function wrong, the input was: {self.get_token()}")

    # region class helper functions

    def get_by_lines(self, input_stream: typing.TextIO):
        # pattern, open, close = r"/\*.*?\*/", "/**", "*/"
        # is_comment = False
        # input_lines = input_stream.read().splitlines()
        # for line in input_lines:
        #     line = line.strip()
        #     if '"' not in line:
        #         line = re.sub(pattern, '', line)
        #     else:
        #         while line.rfind('"') < line.rfind("/*") and line.rfind(
        #                 '/*') < line.rfind("*/"):
        #             line = line[:line.rfind("/*")]
        #     line = line.replace('\t', ' ')
        #     line = line.replace('\\t', ' ')
        #     line = line.strip()
        #     if len(line) != 0 and line[:3] == open:
        #         is_comment = True
        #         continue
        #     if len(line) != 0 and is_comment:
        #         if close in line:
        #             is_comment = False
        #         continue
        #     if close in line:
        #         is_comment = False
        #     if len(line) == 0:
        #         continue
        #     if len(line) != 0 and '/' == line[0] and line[1] == '/':
        #         continue
        #     else:
        #         line_list = line.split(" ")
        #         if '//' in line_list:
        #             comment_idx = line_list.index('//')
        #             list1 = list(line_list[0:comment_idx])
        #             str = " ".join(list1).strip()
        #             if len(str) != 0:
        #                 if '//' in str:
        #                     self.file.append(line[:str.rfind('//')])
        #                 else:
        #                     self.file.append(str)
        #         else:
        #             if len(line) != 0:
        #                 if '//' in line:
        #                     self.file.append(line[:line.rfind('//')])
        #                 else: self.file.append(line)
        pattern = r'/\*.*?\*/'
        is_comment = False
        new_list = []
        for line in self.file:
            line = line.strip()
            if '"' not in line:
                line = re.sub(pattern, '', line)
            line = line.strip()
            if len(line) == 0:
                continue
            if '//' == line[:2]:
                continue
            while line.count('"') >= 2:
                start, end = line.index('"'), find_2th(line)
                new_list.append(line[:start])
                new_list.append(line[start:end + 1])
                if end + 1 >= len(line):
                    continue
                line = line[end + 1:]
            new_list.append(line)
        new_list2 = []
        for l in new_list:
            if len(l) != 0 and l != '/*':
                new_list2.append(l)

        self.file = new_list2

    def remove_slashes(self):
        flag, comment = False, '//'
        for row, line in enumerate(self.file):
            for ind, c in enumerate(line):
                if c == '"':
                    flag = not flag
                if flag:  # ignore what between " "
                    continue
                if ind + 1 < len(line) and line[ind:ind + 2] == comment:
                    self.file[row] = line[:ind]
                    break

    def remove_comments(self):
        pattern = r'/\*.*?\*/'
        flag, comment = False, '*/'
        for row, line in enumerate(self.file):
            self.file[row] = re.sub(pattern, '', line)
        self.file = [x for x in self.file if len(x) != 0]

    def remove_multy_comment(self):

        # / **
        # *Encapsulates a board for the RushHour game.
        # * /
        flag, flag2, close, open, open_multi = False, False, '*/', '/*', '/**'
        for row, line in enumerate(self.file):
            if flag2:
                if close not in line:
                    self.file[row] = open + line + close
                    continue
                else:
                    self.file[row] = line[line.find(close) + 2:]
            for ind, c in enumerate(line):
                if c == '"':
                    flag = not flag
                if flag:  # ignore what between " "
                    continue
                if ind + 1 < len(line) and line[ind:ind + 2] == open:
                    flag2 = True
                if ind + 1 < len(line) and line[ind:ind + 2] == close:
                    temp = open + line
                    self.file[row] = temp
                    flag2 = False

                if (not flag) and c in ['\t', '\\t']:
                    self.file[row] = self.file[row][:ind] + ' ' + line[ind + 1:]
            if flag2:
                self.file[row] = line + close

    def token_word(self, word: str):
        global last_one, temp3

        last_one = ""
        if len(word) == 0:
            return
        elif word in keyword_list:
            self.tokens.append(word)
            return
        elif is_constant_number(word):
            self.tokens.append(word)
            return
        elif check_if_var_name(word):
            self.tokens.append(word)
            return
        elif word[0] in symbol_list:
            self.tokens.append(word[0])
            self.token_word(word[1:])
            return
        else:
            for ind, c in enumerate(word):
                if c in symbol_list:
                    temp = word[:ind]
                    self.tokens.append(word[:ind].strip())
                    self.token_word(word[ind:].strip())
                    return
        last_one = word

    def get_by_tokens(self):
        global temp3
        for ind, line in enumerate(self.file):
            if len(line) != 0 and line[0] == '"':
                self.tokens.append(line)
                continue
            line2 = line.split()
            # if ind< len(self.file)-1 and self.file[ind+1]=='"':
            #     line+='"'
            # if line == '"':
            #     continue
            temp3 = False
            if line.rfind('"') > 0 and line[line.rfind('"') - 1] == ' ':
                temp3 = True

            for word in line2:
                self.token_word(word)

    def connect_strings(self):
        flag = True
        new_list = []
        txt = ""
        last = "."
        for row, symbol in enumerate(self.tokens):
            # if symbol[0] == '"' and symbol[-1] =='"':
            #     new_list.append(symbol.strip())
            #     continue
            #
            # if symbol[0] == '"' and symbol[-1] != '"':
            #     flag = True
            #     txt += symbol
            #     last = symbol
            # elif symbol[-1] == '"':
            #     flag = False
            #     txt += " "
            #     txt += symbol
            #     new_list.append(txt)
            #     txt = ""
            # elif flag:
            #     if symbol not in symbol_list and last not in symbol_list:
            #         txt += " "
            #     txt += symbol
            #     last = symbol
            # else:
            #     new_list.append(symbol.strip())
            if symbol == "do":
                x = 8

            if flag:
                while len(symbol) != 0 and symbol[0] in symbol_list:
                    new_list.append(symbol[0])
                    symbol = symbol[1:]
                if len(symbol) == 0:
                    continue
            if '"' not in symbol and flag:
                new_list.append(symbol)
            else:
                if symbol[0] == '"':
                    if not flag:
                        flag = True
                        txt += " " + symbol
                        new_list.append(txt)
                        txt = ""
                        continue

                    flag = False
                    txt = symbol
                    if symbol[-1] == '"':
                        new_list.append(symbol)
                        flag = True
                        continue
                else:
                    if txt[-1] in symbol_list:
                        txt += " " + symbol
                    if symbol[-1] == '"':
                        flag = True
                        new_list.append(txt)
                        txt = ""
                # if symbol == '"':
        self.tokens = new_list

    def get_token(self):
        if not self.has_more_tokens():
            raise ValueError(
                'has more command function wrong, token out of range"')
        return self.tokens[self.pos]
    # TODO return empty srting instead of raise

    # endregion


def find_2th(string, needle='"', n=2):
    start = string.find(needle)
    while start >= 0 and n > 1:
        start = string.find(needle, start + len(needle))
        n -= 1
    return start
