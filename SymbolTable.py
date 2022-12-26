"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

VAR, ARG, STATIC, FIELD = "VAR", "ARG", "STATIC", "FIELD"
TYPE_IND, KIND_IND, COUNT_IND = 0, 1, 2


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""

        self.count_dic = {ARG: 0, VAR: 0, FIELD: 0, STATIC: 0}
        self.class_symbol_table = {}
        self.subroutine_symbol_table = {}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        # Your code goes here!
        self.count_dic[ARG] = 0
        self.count_dic[VAR] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """

        if kind in [ARG, VAR]:
            self.subroutine_symbol_table[name] = [type, kind, self.var_count(kind)]
        elif kind in [STATIC, FIELD]:
            self.class_symbol_table[name] = [type, kind, self.var_count(kind)]
        self.count_dic[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.count_dic[kind]

    def kind_of(self, name: str) -> typing.Optional[str]:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.subroutine_symbol_table:
            return self.subroutine_symbol_table[name][KIND_IND]
        if name in self.class_symbol_table:
            return self.class_symbol_table[name][KIND_IND]
        return

    def type_of(self, name: str) -> typing.Optional[str]:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # Your code goes here!
        if name in self.subroutine_symbol_table:
            return self.subroutine_symbol_table[name][TYPE_IND]
        if name in self.class_symbol_table:
            return self.class_symbol_table[name][TYPE_IND]
        return

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_symbol_table:
            return self.subroutine_symbol_table[name][COUNT_IND]
        if name in self.class_symbol_table:
            return self.class_symbol_table[name][COUNT_IND]
        raise TypeError(
            f"variable is not known, the var name was{name}")
