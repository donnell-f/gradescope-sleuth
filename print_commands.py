import sqlite3
import os
import platform
from datetime import datetime, timedelta
import re
import functools
import json
from tabulate import tabulate
from pygments.lexers import CppLexer
from pygments.formatters import TerminalFormatter
from pygments import highlight

from .argument_parsing import ArgumentParser, ParsedArguments
from .check_network_settings import check_network_settings, read_config
from .diff_checking import check_diffs
from .print_helpers import download_deliverables

def print_file(colname_fname_dict, parsed_args: ParsedArguments):
    ### NOTE: this code needs major refactoring if -email is added.
    #         Right now, the only id argument is -uin.
    uin = parsed_args.get_argument('-uin')
    file_name = parsed_args.get_argument('-file')
    no_line_nums = parsed_args.get_argument('-nonums')

    if (uin == False):
        raise NameError("Please provide at least one form of identification (only -uin supported right now).")
    else:
        uin = int(uin[0])
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



def print_history(colname_fname_dict, parsed_args: ParsedArguments):
    # fname_colname_dict = {colname_fname_dict[k]: k for k in colname_fname_dict}

    uin = parsed_args.get_argument('-uin')
    email = parsed_args.get_argument('-email')

    if (uin == False and email == False):
        raise NameError("You must provide a UIN or email to identify a student.")
    elif (uin == True and email == True):
        raise NameError("Identify student by either -email or -uin but not both.")
    else:
        if (uin != False):
            uin = int(uin[0])
        elif (email != False):
            email = email[0].strip()

    conn = sqlite3.connect("submissions_db.db")
    curs = conn.cursor()

    if (email != False):
        curs.execute("SELECT submission_history, student_name, uin FROM submissions WHERE email = ?", (email,))
    elif (uin != False):
        curs.execute("SELECT submission_history, student_name, uin FROM submissions WHERE uin = ?", (uin,))
    res = curs.fetchall()
    if (len(res) > 1):
        raise ValueError("`print history` found two students with the same uin???")
    if (len(res[0]) > 3):
        raise ValueError("Wrong query in `print history`.")
    name_uin = f"{res[0][1]} ({res[0][2]})"
    sub_hist = json.loads(res[0][0])

    # Make sure all the network nettings are functional
    check_network_settings()

    config_dict = read_config()

    # Downloads all deliverables, modifying sub_hist
    download_deliverables(sub_hist, colname_fname_dict, config_dict, name_uin)
    
    print()
    print(f"Submission history for {name_uin}")
    print()
    
    # Print initial submission "diff"
    time_delta_str = f"{round(sub_hist[0]['time_delta'] / 3600, 2)} hrs" if sub_hist[0]['time_delta'] / 3600 >= 1 else f"{round(sub_hist[0]['time_delta'] / 60)} mins"
    print(f"\033]8;;{sub_hist[0]['link']}\033\\{"Submission 1"}\033]8;;\033\\")
    print(f"Created: {sub_hist[0]['created_at']}. Delta: +{time_delta_str}.")
    print(f"Score: {round(sub_hist[0]['score'], 2)} pts.")
    files_submitted = [d for d in sub_hist[0]['deliverables'] if sub_hist[0]['deliverables'][d] != ""]
    print("Files submitted:")
    for fs in files_submitted:
        print(f"    - {colname_fname_dict[fs]}")
    print()

    # Print the actual diffs
    for shi in range(1, len(sub_hist)):
        time_delta_str = f"{round(sub_hist[shi]['time_delta'] / 3600, 2)} hrs" if sub_hist[shi]['time_delta'] / 3600 >= 1 else f"{round(sub_hist[shi]['time_delta'] / 60)} mins"
        print(f"\033]8;;{sub_hist[shi]['link']}\033\\{f"Submission {shi+1}"}\033]8;;\033\\")
        print(f"Created: {sub_hist[shi]['created_at']}. Delta: +{time_delta_str}.")
        print(f"Score: {round(sub_hist[shi]['score'], 2)} pts.")
        for cn in colname_fname_dict:
            print(f"{colname_fname_dict[cn]}:")
            diff_dict = check_diffs(sub_hist[shi-1]['deliverables'][cn], sub_hist[shi]['deliverables'][cn])
            print(f"    - Added {diff_dict['added']} lines.")
            print(f"    - Removed {diff_dict['removed']} lines.")
            print(f"    - Changed {diff_dict['changed']} lines.")
        print()





    
    
    



