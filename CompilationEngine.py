"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
# import os
# import typing
import VMWriter
import SymbolTable

# "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"

T_types_dic = {"INT_CONST": "integerConstant", "SYMBOL": "symbol",
               "IDENTIFIER": "identifier", "KEYWORD": "keyword",
               "STRING_CONST": "stringConstant"}

keyWords = {'boolean': 'BOOLEAN', 'char': 'CHAR', 'class': 'CLASS',
            'constructor': 'CONSTRUCTOR', 'do': 'DO', 'else': 'ELSE',
            'false': 'FALSE', 'field': 'FIELD', 'function': 'FUNCTION', 'if': 'IF',
            'int': 'INT', 'let': 'LET', 'method': 'METHOD', 'null': 'NULL',
            'return': 'RETURN', 'static': 'STATIC', 'this': 'THIS', 'true': 'TRUE',
            'var': 'VAR', 'void': 'VOID', 'while': 'WHILE'}

symbols = \
    {'&', '(', ')', '*', '+', ',', '-', '.', '/', ';', '<', '=', '>', '[', ']',
     '{', '|', '}', '~'}

keyword_switch = \
    {'BOOLEAN': 'boolean', 'CHAR': 'char', 'CLASS': 'class',
     'CONSTRUCTOR': 'constructor', 'DO': 'do', 'ELSE': 'else',
     'FALSE': 'false', 'FIELD': 'field', 'FUNCTION': 'function', 'IF': 'if',
     'INT': 'int', 'LET': 'let', 'METHOD': 'method', 'NULL': 'null',
     'RETURN': 'return', 'STATIC': 'static', 'THIS': 'this', 'TRUE': 'true',
     'VAR': 'var', 'VOID': 'void', 'WHILE': 'while'}
op_switch = {'+': "add", '-': "sub", '*': "call Math.multiply 2", '/': "call Math.divide 2",
             '&': "and", '|': "or", '<': "lt", '>': "gt", '=': "eq"}
symbol_switch = \
    {'&': '&amp;', '(': '(', ')': ')', '*': '*', '+': '+', ',': ',', '-': '-',
     '.': '.', '/': '/', '\"': '', ';': ';', '<': '&lt;', '=': '=',
     '>': '&gt;', '[': '[', ']': ']', '{': '{', '|': '|', '}': '}', '~': '~'}
NOT_EXIST = -1
VAR, ARG, STATIC, FIELD = "VAR", "ARG", "STATIC", "FIELD"
local, var, arg, static, field, constant = "local", "var", "arg", "static", "field", "constant"
function, constructor, method = "function", "constructor", "method"
pointer, this, that, argument = "pointer", "this", "that", "argument"

op_list = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
unary_op_list = ['-', '~']
keyword_constant = ["true", "false", "null", "this"]

brackets_dic = {'{': '}', '[': ']', '(': ')'}

clasess_list = []


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def compile_token(self):
        token, token_type = self.get_token(), \
                            self.JackTokenizer.token_type()
        self.os.write(f"<{token}>")

        self.os.write(f"</{token}>")

    def __init__(self, input_stream: "JackTokenizer", output_stream,dic:dict) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.token, self.token_type, self.class_name, self.subrourtine_type = "", "", "", ""
        self.JackTokenizer = input_stream
        self.os = output_stream
        self.spaces = ""
        self.statments_type = {"let": self.compile_let,
                               "if": self.compile_if,
                               "while": self.compile_while,
                               "do": self.compile_do,
                               "return": self.compile_return}
        self.vm = VMWriter.VMWriter(output_stream)
        self.symbol_table = SymbolTable.SymbolTable()
        self.methods_dic = dic

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # class class_name {class_var_dec* subroutine_dec*}
        self.write("//class declare")
        self.advance()  # class
        self.class_name = self.get_token_and_advance()  # class name
        self.advance()  # {
        self.write("//declare class var")
        while self.get_token() in ["field", "static"]:
            self.compile_class_var_dec()
            self.advance()
        while self.get_token() in ["method", "function", "constructor"]:
            self.compile_subroutine()
            self.advance()
        self.advance()  # }

    def compile_class_var_dec(self) -> None:

        """Compiles a static declaration or a field declaration."""
        # static|field type var_name (,var_name)* ;

        kind = self.JackTokenizer.keyword()  # var kind: static | field
        self.advance()

        type = self.get_token_and_advance()  # var type: int | boolean...
        name = self.get_token_and_advance()  # var name
        self.symbol_table.define(name, type, str(kind).upper())
        while self.get_token() == ',':
            self.advance()
            name = self.get_token()  # var name
            self.symbol_table.define(name, type, str(kind).upper())
            self.advance()
        # self.advance()  # ;

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # cons|mthod|function void|type subroutine_name
        # ( parameted_list ) subroutine_body
        # subroutine body: {var_dce* statments}.
        self.symbol_table.start_subroutine()
        self.subrourtine_type = self.get_token(), self.get_token()  # cons|method|function
        self.advance()
        if self.subrourtine_type == method:
            self.symbol_table.define(this, self.class_name, ARG)  # add the object to the sym_dictionary
        if self.get_token() in keyWords.keys():  # return type
            type = self.keyword_and_advance()  # exist return type
        else:
            type = self.identifier_and_advance()  # new return type  # void|type

        subroutine_name = self.get_token_and_advance()  # function name
        self.advance()  # (
        self.compile_parameter_list()  # parameted_list
        self.double_advance()  # ')' and '{'
        while self.get_token() == var:
            self.compile_var_dec()
            self.advance()
        self.vm.write_function(f"{self.class_name}.{subroutine_name}", self.symbol_table.var_count(VAR))  # function name n_lcl
        if self.subrourtine_type == constructor:
            self.compile_constuctor()
        else:
            self.compile_function_and_method()
        self.compile_statements()
        self.print_symbol()  # }

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()" go until the one next to the end of the list.
        """
        # ((type var_name)  (,var_name)*)?
        # Your code goes here!
        type = ""

        if self.get_token() != ')':
            if self.get_token() in keyWords.keys():  # exist type
                type = self.keyword_and_advance()
            elif self.get_token().isidentifier():  # new type
                type = self.identifier_and_advance()
            name = self.identifier_and_advance()  # var_name
            # ',' or ')'

            self.add_variable(name, type, ARG)

            while self.get_token() == ',':  # skip on ','
                self.advance()
                if self.get_next_token() not in [',', ')']:
                    if self.get_token() in keyWords.keys():  # exist type
                        type = self.keyword_and_advance()
                    elif self.get_token().isidentifier():  # new type
                        type = self.identifier_and_advance()

                name = self.identifier_and_advance()  # var_name
                self.add_variable(name, type, ARG)

    def compile_var_dec(self) -> None:
        # field|static type car_name (,var_name)* ;
        # self.print_keyword_and_advance()
        kind = self.keyword_and_advance()  # var

        if self.get_token() in keyWords.keys():
            type = self.keyword_and_advance()  # exist type
        else:
            type = self.identifier_and_advance()  # new type
        name = self.identifier_and_advance()  # var_name
        self.add_variable(name, type, VAR)
        while self.get_token() == ",":
            if self.get_token() in keyWords.keys():
                type = self.keyword_and_advance()  # exist type
            else:
                type = self.identifier_and_advance()  # new type
            name = self.identifier_and_advance()  # var_name
            self.add_variable(name, type, VAR)

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """

        while self.get_token() in self.statments_type.keys():
            self.statments_type[self.get_token()]()
            self.advance()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # do subroutine call
        self.advance()  # do
        self.subroutine_call()
        self.vm.write_push(constant, 0)
        self.vm.write_return()
        pass  # ;

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.open_main_xml("letStatement")
        self.print_keyword_and_advance()  # let
        self.print_identifier_and_advance()  # var_name
        if self.get_token() == '[':
            self.print_symbol_and_advance()
            self.compile_expression()
            self.print_symbol_and_advance()
        self.print_symbol_and_advance()  # =
        self.compile_expression()
        self.print_symbol()  # ;
        self.close_main_xml("letStatement")
        # TODO

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # while (expression) {statments}
        self.open_main_xml("whileStatement")
        self.print_keyword_and_advance()  # while
        self.print_symbol_and_advance()  # (
        self.compile_expression()  # expression
        self.print_symbol_and_advance()  # )
        self.print_symbol_and_advance()  # {
        self.compile_statements()  # statemants
        self.print_symbol()  # }
        self.close_main_xml("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.open_main_xml("returnStatement")
        self.print_and_advance()
        if self.get_token() != ';':
            self.compile_expression()
            # self.advance()
        self.print_symbol()
        self.close_main_xml("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # if (expression) {statments} (else {statements})?
        self.open_main_xml("ifStatement")
        self.print_keyword_and_advance()  # if
        self.print_symbol_and_advance()  # (
        self.compile_expression()  # expressions
        self.print_symbol_and_advance()  # )
        self.print_symbol_and_advance()  # {
        self.compile_statements()  # statements
        self.print_symbol_and_advance()  # }
        if self.get_token() == "else":
            self.print_keyword_and_advance()  # else
            self.print_symbol_and_advance()  # {
            self.compile_statements()  # statements
            self.print_symbol_and_advance()  # }
            a = self.JackTokenizer.tokens[self.JackTokenizer.pos]
            a = a

        self.back()
        self.close_main_xml("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # term op term op term...
        self.compile_term()
        self.advance()
        while self.get_token() in op_list:
            op = self.get_token_and_advance()
            self.compile_term()
            self.write(op_switch[op])
            self.advance()

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!

        # self.advance()
        token_type, token = self.JackTokenizer.token_type(), self.get_token()
        if token_type == "INT_CONST":
            self.vm.write_push("constant", int(token))
        elif token_type == "STRING_CONST":
            self.compile_string(token)
        elif token_type == "KEYWORD" and token in keyword_constant:
            self.compile_keyword_constant(token)
        elif token_type == "IDENTIFIER":
            self.term_identifier_product()
        elif token == "(":
            self.advance()
            self.compile_expression()
        elif token in unary_op_list:
            temp_op = self.get_token_and_advance()
            self.compile_term()
            self.write(temp_op)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # (expression (,expression)*)?
        flag = False
        counter = 0
        if self.get_token() != ')':  # possibly empty
            flag = True
            counter += 1
            # push to stack so we can send it to the function
            self.compile_expression()
            while self.get_token() == ",":
                counter += 1
                self.advance()  # ,
                # push to stack so we can send it to the function
                self.compile_expression()
        return counter

    # **************************** helper functions ***************************

    def subroutine_call(self):
        args_count = 0
        name = self.identifier_and_advance()  # var|class_name
        if self.get_token() == '.':  # var|class . subroutine name
            self.advance()  # '.'
            subroutine_name = self.identifier_and_advance()  # var|class_name method name
            self.advance()  # (
            self.compile_expression_list()  # expression
            self.advance()  # )
        elif self.get_token() == '(':  # subroutine_name(expression)
            self.advance()  # '('
            self.compile_expression_list()
            self.advance()  # ')'

    def term_identifier_product(self):
        # self.advance()
        name = self.get_token_and_advance()  # class|var name
        if self.get_token() == '[':  # var [expression] #TODO שייך למערכים
            self.advance()  # [
            self.compile_expression()  # expression
            pass  # ]
        elif self.get_token() == '.':  # var|class . subroutine name
            self.compile_method_call(name)
        elif self.get_token() == '(':  # subroutine_name(expression)
            self.advance()  # (
            argument_amount = self.compile_expression_list()  # expression
            self.vm.write_call(name, argument_amount)
            pass  # )
        else:  # var name
            self.compile_var(name)
            self.back()

    # region old functions
    def add_type_and_token(self, tokens_list, types_list):
        tokens_list.append(self.get_token())
        types_list.append(self.JackTokenizer.token_type())

    def add_spaces(self):
        self.spaces += "  "

    def remove_spaces(self):
        self.spaces = self.spaces[:-2]

    def print_to_file(self, txt: str):
        self.os.write(self.spaces + txt)

    def print_and_advance(self):
        token = self.get_token()  # add 'field'
        token_type = self.JackTokenizer.token_type()
        self.advance()
        self.os.write(
            self.spaces + f"<{T_types_dic[token_type]}> {token} </{T_types_dic[token_type]}>\n")

    def open_xml(self, txt):
        self.os.write(self.spaces + f"<{txt}>")

    def close_xml(self, txt):
        self.os.write(f"</{txt}>\n")

    def open_main_xml(self, txt):
        x = txt + '\n'
        self.open_xml(txt)
        self.os.write('\n')
        self.add_spaces()

    def close_main_xml(self, txt):
        self.remove_spaces()
        x = self.spaces + txt
        self.os.write(f"{self.spaces}</{txt}>\n")

    def term_type(self):
        # "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        token_type = self.JackTokenizer.token_type()
        if token_type in ["INT_CONST", "STRING_CONST"]:
            return token_type

    def print_int_constant(self):
        self.open_xml("integerConstant")
        self.os.write(f" {self.JackTokenizer.int_val()} ")
        self.close_xml("integerConstant")

    def print_str_constant(self):
        self.open_xml("stringConstant")
        self.os.write(f" {self.JackTokenizer.string_val()} ")
        self.close_xml("stringConstant")

    def print_keyword_constant(self):
        self.open_xml("keyword")
        temp1 = self.JackTokenizer.keyword()
        self.os.write(f" {keyword_switch[self.JackTokenizer.keyword()]} ")
        self.close_xml("keyword")

    def print_keyword_and_advance(self):
        self.print_keyword_constant()
        self.advance()

    def down_line(self):
        self.print_to_file("\n")

    def get_token(self):
        return self.JackTokenizer.get_token()

    def get_type(self):
        return self.JackTokenizer.get_type()

    def advance(self):
        self.JackTokenizer.advance()

    def back(self):
        self.JackTokenizer.back()

    def print_symbol(self):
        self.open_xml("symbol")
        temp1 = self.JackTokenizer.get_token()
        self.os.write(f" {symbol_switch[self.JackTokenizer.symbol()]} ")
        self.close_xml("symbol")

    def print_symbol_and_advance(self):
        self.print_symbol()
        self.advance()

    def print_identifier(self):
        self.open_xml("identifier")

        self.os.write(f" {self.JackTokenizer.identifier()} ")
        self.close_xml("identifier")

    def print_identifier_and_advance(self):
        self.print_identifier()
        self.advance()

    def get_next_token(self):
        self.advance()
        temp = self.get_token()
        self.back()
        return temp

    def compile_expression_and_advance(self):
        self.compile_expression()
        self.advance()

    def compile_statements_and_advance(self):
        self.compile_statements()
        self.advance()

    def print_var_type(self):
        if self.get_token() in keyWords.keys():
            self.print_keyword_and_advance()  # exist type
        else:
            self.print_identifier_and_advance()

    def print_last_symbol(self):
        self.back()
        self.print_symbol_and_advance()

    def compile_expression_list_and_advance(self):
        self.compile_expression_list()
        self.advance()

    def write(self, txt):
        self.os.write(txt + '\n')

    def double_advance(self):
        self.advance()
        self.advance()

    def triple_advance(self):
        self.double_advance()
        self.advance()

    def keyword_and_advance(self):
        temp = self.JackTokenizer.keyword()
        self.advance()
        return temp

    def symbol_and_advance(self):
        temp = self.JackTokenizer.symbol()
        self.advance()
        return temp

    def identifier_and_advance(self):
        temp = self.JackTokenizer.identifier()
        self.advance()
        return temp

    # endregion
    def add_variable(self, name, type, kind):
        self.symbol_table.define(name, type, kind)

    def get_token_and_advance(self):
        temp = self.get_token()
        self.advance()
        return temp

    def compile_constuctor(self):

        self.vm.write_push("constant", self.symbol_table.var_count("FIELD"))
        self.vm.write_call(f"Memory.alloc", 1)
        self.vm.write_pop("pointer", 0)

    def compile_function_and_method(self):
        self.vm.write_push(argument, 0)  # push the object to argument 0
        self.vm.write_pop(pointer, 0)

    def compile_string(self, txt: str):
        self.vm.write_push("constant", len(txt))
        self.vm.write_call("String.new", 1)
        for c in txt:
            self.vm.write_push("constant", ord(c))
            self.vm.write_call("appendChar", 2)
        # for c in txt:

    def compile_keyword_constant(self, key: str):
        if key in ["null", "false"]:
            self.vm.write_push(constant, 0)
        elif key == "true":
            self.vm.write_push(constant, 1)
            self.vm.write_arithmetic("NEG")
        elif key == this:
            self.vm.write_push(pointer, 0)

    def compile_var(self, name: str):
        kind, index = self.symbol_table.kind_of(name), self.symbol_table.index_of(name)
        if kind == ARG.upper():
            self.vm.write_push(argument, index)
        elif kind == VAR.upper():
            self.vm.write_push(local, index)
        elif kind == FIELD.upper():
            self.vm.write_push(this, index)
        elif kind == STATIC.upper():
            self.vm.write_push(static, index)
        else:
            raise TypeError(
                f"var kind of '{name}' is not known, \n"
                f"the var kind of {name} was {name} and the index was {index}")

    def compile_method_call(self, name: str):
        """
        in case of var|class.fun(exp)
        push the nedded vars and call the function
        """
        self.advance()  # .
        argument_amount = 0
        sub_name = self.get_token_and_advance()  # sub_name
        self.advance()  # (
        kind=self.symbol_table.kind_of(name)
        if kind and self.methods_dic[kind][sub_name] == method:
            self.vm.write_push("this", 0)
            argument_amount += 1  # send this 0 as well
        # check how much variable in the brackets and *push them*
        argument_amount += self.compile_expression_list()
        if self.get_token() != ')':
            self.advance()  # empty
        self.vm.write_call(name, argument_amount)
        pass  # )

