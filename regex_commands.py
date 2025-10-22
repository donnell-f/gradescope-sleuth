import yaml
import sqlite3
import os
import platform
from datetime import datetime
import json
import re
import functools
from tabulate import tabulate
from enum import Enum

from .argument_parsing import ArgumentParser, ParsedArguments
from .regex_backend import get_in_context_matches


# Added LRU cache for speed
@functools.lru_cache(maxsize=256)
def _compile_cinsensitive(pat):
    return re.compile(pat, re.IGNORECASE)
@functools.lru_cache(maxsize=256)
def _compile_csensitive(pat):
    return re.compile(pat)

# Define two implementations of the regex function: one for case insensitive, and one for case sensitive
def py_regexp_cinsensitive(pattern, value):
    if pattern is None or value is None:
        return 0
    try:
        return 1 if _compile_cinsensitive(pattern).search(str(value)) else 0
    except re.error:
        return 0
def py_regexp_csensitive(pattern, value):
    if pattern is None or value is None:
        return 0
    try:
        return 1 if _compile_csensitive(pattern).search(str(value)) else 0
    except re.error:
        return 0

def print_matching_database_rows(pattern, row_matches, deliv_cols, deliv_files, case_sensitive, first_only, out_file, match_number_enabled: bool):
    # Set up out_file depending on what was passed in
    if (out_file != False):
        out_file = out_file[0]

    # Open file in parent dir if given
    # Delete it if it already exists
    if os.path.exists(f"../{out_file}"):
        os.remove(f"../{out_file}")
    outf = open(f"../{out_file}", "a")

    # Iterate through each returned row from the database
    # Print the actual in-context matches for deliverable columns' data
    for rmi in range(len(row_matches)):
        student_name = row_matches[rmi][0 + len(deliv_cols) + 1]
        uin = row_matches[rmi][0 + len(deliv_cols) + 2]
        email = row_matches[rmi][0 + len(deliv_cols) + 3]

        for k in range(len(deliv_cols)):
            # Print to screen
            print(
                get_in_context_matches(
                    pattern,
                    row_matches[rmi][1 + k],
                    student_name,
                    uin,
                    email,
                    deliv_files[k],
                    match_number_enabled,
                    rmi + 1,
                    case_sensitive,
                    pretty_printing=True,
                    first_only=first_only
                ),
                end=''
            )

            # Print to file (optional)
            if (out_file != False):
                outf.write(
                    get_in_context_matches(
                        pattern,
                        row_matches[rmi][1 + k],
                        student_name,
                        uin,
                        email,
                        deliv_files[k],
                        match_number_enabled,
                        rmi + 1,
                        case_sensitive,
                        pretty_printing=False,
                        first_only=first_only
                    )
                )

        # Separate match results
        if (rmi != len(row_matches) - 1):
            print("\n\n\n\n\n", end='')
            if (out_file != False):
                outf.write('\n\n\n\n\n')
        
        outf.close()



def regex_all(deliverables: dict[str,str], parsed_args: ParsedArguments):
    deliv_cols = list(deliverables.keys())
    deliv_files = [deliverables[dc] for dc in deliv_cols]

    # Get args
    case_sensitive = parsed_args.get_argument('-case')
    verbose = parsed_args.get_argument('-v')
    first_only = parsed_args.get_argument('-f')
    out_file = parsed_args.get_argument('-outf')
    pattern = parsed_args.get_remainder()

    # Set up out_file
    if (out_file != False):
        out_file = out_file[0]

    # Make sure arguments make actual sense
    if (first_only and (not verbose)):
        raise ValueError("Bad args -- the argument -f requires -v.")

    conn = sqlite3.connect("submissions_db.db")

    # Define REGEXP function based on -csens argument
    if (case_sensitive):
        conn.create_function("regexp", 2, py_regexp_csensitive, deterministic=True)
    else:
        conn.create_function("regexp", 2, py_regexp_cinsensitive, deterministic=True)
    
    curs = conn.cursor()
    
    conditions = [f"{d} REGEXP ?" for d in deliv_cols]
    condition_string = " OR ".join(conditions)
    pattern_tuple = tuple(pattern for _ in range(len(conditions)))

    if (not verbose):
        # Print all student submissions matching pattern and then return
        curs.execute(f"SELECT student_name, uin, email FROM submissions WHERE {condition_string}", pattern_tuple)
        print(tabulate([("Name", "UIN", "E-Mail")] + curs.fetchall(), headers="firstrow", tablefmt="psql"))
        return

    if (verbose):
        curs.execute(f"SELECT * FROM submissions WHERE {condition_string}", pattern_tuple)
        row_matches = curs.fetchall()

        print_matching_database_rows(pattern, row_matches, deliv_cols, deliv_files, case_sensitive, first_only, out_file, match_number_enabled=True)
        return



def regex_one(deliverables: dict[str,str], parsed_args: ParsedArguments):
    deliv_cols = list(deliverables.keys())
    deliv_files = [deliverables[dc] for dc in deliv_cols]

    # Get args
    case_sensitive = parsed_args.get_argument('-case')
    uin_arg = parsed_args.get_argument('-uin')
    email_arg = parsed_args.get_argument('-email')
    first_only = parsed_args.get_argument('-f')
    out_file = parsed_args.get_argument('-outf')
    pattern = parsed_args.get_remainder()

    # Set up args
    if (out_file != False):
        out_file = out_file[0]
    if (uin_arg != False):
        uin_arg = uin_arg[0]
    if (email_arg != False):
        email_arg = email_arg[0]
    
    # Validate args
    id_arg_count = 0
    id_type_colname = None
    id_value = None
    if (uin_arg != False):
        id_arg_count += 1
        id_type_colname = 'uin'
        id_value = uin_arg
    if (email_arg != False):
        id_arg_count += 1
        id_type_colname = 'email'
        id_value = email_arg
    if (id_arg_count > 1):
        raise ValueError("Too many id arguments. You must identify a student using exactly one form of id.")
    if (id_arg_count < 1):
        raise ValueError("Too few id arguments. You must identify a student using exactly one form of id.")

    conn = sqlite3.connect("submissions_db.db")

    # Define REGEXP function based on -csens argument
    if (case_sensitive):
        conn.create_function("regexp", 2, py_regexp_csensitive, deterministic=True)
    else:
        conn.create_function("regexp", 2, py_regexp_cinsensitive, deterministic=True)
    
    curs = conn.cursor()

    curs.execute(f"SELECT * FROM submissions WHERE {id_type_colname} = ?", (id_value,))
    row_matches = curs.fetchall()

    if (len(row_matches) == 0):
        raise NameError("Could not find that student in the database.")

    print_matching_database_rows(pattern, row_matches, deliv_cols, deliv_files, case_sensitive, first_only, out_file, match_number_enabled=False)
    return



