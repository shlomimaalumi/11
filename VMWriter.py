"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

arithmetic_switch = {"ADD": 'add', "SUB": 'sub', "NEG": 'neg',
                     "EQ": "eq", "GT": "gt", "LT": "lt", "AND": "and", "OR": "or",
                     "NOT": "not", "SHIFTLEFT": "shiftleft", "SHIFTRIGHT": "shiftright"}


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.os = output_stream
        # output_stream.write("Hello world! \n")
        pass

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        self.write(f"push {segment} {index}")

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        self.write(f"pop {segment} {index}")

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        self.write(arithmetic_switch[command])

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        # Your code goes here!
        self.write(f"label {label}")

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.
        Args:
            label (str): the label to go to.
        """
        # Your code goes here!
        self.write(f"goto {label}")

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        # Your code goes here!
        self.write(f"if-goto {label}")

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.write(f"call {name} {n_args}")
        # Your code goes here!

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        # Your code goes here!
        self.write(f"function {name} {n_locals}")
        pass

    def write_return(self) -> None:
        """Writes a VM return command."""
        # Your code goes here!
        self.write("return")

    # region helper function

    def write(self, str):
        self.os.write(str+'\n')
    # endregion
