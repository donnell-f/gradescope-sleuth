import sqlite3
import os
import platform
from datetime import datetime, timedelta
import re
import functools
from tabulate import tabulate
from pygments.lexers import CppLexer
from pygments.formatters import TerminalFormatter
from pygments import highlight

from .argument_parsing import ArgumentParser, ParsedArguments

def print_student(colname_fname_dict, parsed_args: ParsedArguments):
    ### NOTE: this code needs major refactoring if -email is added.
    #         Right now, the only id argument is -uin.
    uin = parsed_args.get_argument('-uin')
    file_name = parsed_args.get_argument('-file')
    no_line_nums = parsed_args.get_argument('-nonums')

    if (uin == False):
        raise NameError("Please provide at least one form of identification (only -uin supported right now).")
    else:
        uin = uin[0]
    if (file_name == False):
        raise NameError("Please profile a deliverable file name with -file")
    else:
        file_name = file_name[0]

    fname_colname_dict = {colname_fname_dict[cfd]: cfd for cfd in colname_fname_dict}
    file_names = list(fname_colname_dict.keys())

    # Make sure -file exists
    if (file_name not in file_names):
        raise NameError("Invalid file name.")
    
    conn = sqlite3.connect("submissions_db.db")
    curs = conn.cursor()

    curs.execute("SELECT * FROM submissions WHERE uin = ?", (uin,))
    query_results = curs.fetchall()

    # Make pretty code
    file_code = query_results[0][1 + file_names.index(file_name)]
    lexer = CppLexer(stripnl=False)
    formatter = TerminalFormatter(style='default')
    pretty_file_code = highlight(file_code, lexer, formatter)
    pretty_file_split = pretty_file_code.split('\n')
    max_line_num = len(pretty_file_split) + 1
    len_max_line_num = len(str(max_line_num))
    output_code = None
    if (no_line_nums):
        output_code = [ ln for ln in pretty_file_split ]
    else:
        output_code = [ f"{str(li+1).ljust(len_max_line_num)} │ {pretty_file_split[li]}" for li in range(len(pretty_file_split))]

    name = query_results[0][1 + len(colname_fname_dict) + 0]
    # uin = query_results[0][1 + len(colname_fname_dict) + 1]
    email = query_results[0][1 + len(colname_fname_dict) + 2]

    print(f"{name}, {uin}, {email}  -  {file_name}")
    print()
    print("\n".join(output_code))





