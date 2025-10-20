import yaml
import sqlite3
import os
import platform
from datetime import datetime
import json
import re
import functools
from .argument_parsing import ArgumentParser

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


def regex_all(deliverable_colnames, argparser: ArgumentParser):
    case_sensitive = argparser.get_argument('-csens')
    verbose = argparser.get_argument('-v')
    first_only = argparser.get_argument('-f')

    # Sanity check the parsed arguments
    if (first_only and (not verbose)):
        raise ValueError("Bad args -- \'-f\' requires \'-v\'.")

    conn = sqlite3.connect("submissions_db.db")

    # Define REGEXP function based on -csens argument
    if (case_sensitive):
        conn.create_function("regexp", 2, py_regexp_csensitive, deterministic=True)
    else:
        conn.create_function("regexp", 2, py_regexp_cinsensitive, deterministic=True)
    
    curs = conn.cursor()
    
    row_matches = None
    conditions = [f"{d} REGEXP ?" for d in deliverable_colnames]
    condition_string = " OR ".join(conditions)
    pattern_tuple = tuple(pattern for _ in range(len(conditions)))
    if verbose:
        print("Verbose not working yet. Try again later.")
    else:
        # Print all student submissions matching pattern
        curs.execute(f"SELECT (student_name, uin, email) FROM submissions WHERE {condition_string}", pattern_tuple)
        row_matches = curs.fetchall()
        for rm in row_matches:
            print(rm[0], rm[1], rm[2])


