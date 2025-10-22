import yaml
import sqlite3
import os
import platform
from datetime import datetime
import json
import re
import functools
from tabulate import tabulate

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


def regex_all(deliverables: dict[str,str], parsed_args: ParsedArguments):
    deliv_cols = list(deliverables.keys())
    deliv_files = [deliverables[dc] for dc in deliv_cols]

    case_sensitive = parsed_args.get_argument('-case')
    verbose = parsed_args.get_argument('-v')
    first_only = parsed_args.get_argument('-f')
    out_file = parsed_args.get_argument('-outf')
    if (out_file != False):
        out_file = out_file[0]
    pattern = parsed_args.get_remainder()

    # Open file in parent dir if given
    # Delete it if it already exists
    if os.path.exists(f"../{out_file}"):
        os.remove(f"../{out_file}")
    outf = open(f"../{out_file}", "a")

    # Make sure arguments make actual sense
    if (first_only and (not verbose)):
        raise ValueError("Bad args -- \'-f\' requires \'-v\'.")

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

        for rmi in range(len(row_matches)):
            student_name = row_matches[rmi][0 + len(deliverables) + 1]
            uin = row_matches[rmi][0 + len(deliverables) + 2]
            email = row_matches[rmi][0 + len(deliverables) + 3]

            for k in range(len(deliv_cols)):
                print(
                    get_in_context_matches(
                        pattern,
                        row_matches[rmi][1 + k],
                        student_name,
                        uin,
                        email,
                        deliv_files[k],
                        rmi + 1,
                        case_sensitive,
                        pretty_printing=True,
                        first_only=first_only
                    ),
                    end=''
                )
                if (out_file != False):
                    outf.write(
                        get_in_context_matches(
                            pattern,
                            row_matches[rmi][1 + k],
                            student_name,
                            uin,
                            email,
                            deliv_files[k],
                            rmi + 1,
                            case_sensitive,
                            pretty_printing=False,
                            first_only=first_only
                        )
                    )

            if (rmi != len(row_matches) - 1):
                print("\n\n\n\n\n", end='')
                if (out_file != False):
                    outf.write('\n\n\n\n\n')

        return




