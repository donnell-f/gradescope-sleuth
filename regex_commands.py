import sqlite3
import os
import platform
from datetime import datetime
import re
from tabulate import tabulate

from .argument_parsing import ArgumentParser, ParsedArguments
from .regex_backend import get_in_context_matches, py_regexp_cinsensitive, py_regexp_csensitive

def print_matching_database_rows(pattern, row_matches, deliv_cols, deliv_files, case_sensitive, first_only, out_file, match_number_enabled: bool, context_radius: int):
    # Open file in parent dir if given
    # Delete it if it already exists
    
    outf_string = ""

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
                    first_only=first_only,
                    context_radius=context_radius
                ),
                end=''
            )

            # Print to file (optional)
            if (out_file != False):
                outf_string += get_in_context_matches(
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
                        first_only=first_only,
                        context_radius=context_radius
                    )

        # Separate match results
        if (rmi != len(row_matches) - 1):
            print("\n\n\n\n\n", end='')
            if (out_file != False):
                outf_string += '\n\n\n\n\n'
        
        # Write the output string to the file
        if (out_file != False):
            with open(f"../{out_file}", "w") as f:
                f.write(outf_string)



def regex_all(deliverables: dict[str,str], parsed_args: ParsedArguments):
    deliv_cols = list(deliverables.keys())
    deliv_files = [deliverables[dc] for dc in deliv_cols]

    # Get args
    case_sensitive = parsed_args.get_argument('-case')
    verbose = parsed_args.get_argument('-v')
    first_only = parsed_args.get_argument('-f')
    out_file = parsed_args.get_argument('-outf')
    simple_output = parsed_args.get_argument('-simple')
    context_radius = parsed_args.get_argument('-crad')
    pattern = parsed_args.get_remainder()

    if (context_radius != False):
        context_radius = int(context_radius[0])
    else:
        # Default to 1
        context_radius = 1

    # Set up out_file
    if (out_file != False):
        out_file = out_file[0]

    # Make sure arguments make actual sense
    if (first_only and (not verbose)):
        raise NameError("Bad args -- the argument -f requires -v.")
    if (simple_output and verbose):
        raise NameError("Output cannot be both simple and verbose. Remove -v or -simple.")

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
        row_matches = curs.fetchall()
        print(f"{len(row_matches)} matching students.")
        if (not simple_output):
            print(tabulate([("Name", "UIN", "E-Mail")] + row_matches, headers="firstrow", tablefmt="psql"))
        else:
            for mr in row_matches:
                print(f"{mr[0]}, {mr[1]}")
        return

    if (verbose):
        curs.execute(f"SELECT * FROM submissions WHERE {condition_string}", pattern_tuple)
        row_matches = curs.fetchall()

        print(f"{len(row_matches)} matching students...")

        print_matching_database_rows(pattern, row_matches, deliv_cols, deliv_files, case_sensitive, first_only, out_file, match_number_enabled=True, context_radius=context_radius)
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
    context_radius = parsed_args.get_argument('-crad')
    pattern = parsed_args.get_remainder()

    # Check out context radius
    if (context_radius != False):
        context_radius = int(context_radius[0])
    else:
        # Default to 1
        context_radius = 1

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
        raise NameError("Too many id arguments. You must identify a student using exactly one form of id.")
    if (id_arg_count < 1):
        raise NameError("Too few id arguments. You must identify a student using exactly one form of id.")

    conn = sqlite3.connect("submissions_db.db")

    # Define REGEXP function based on -csens argument
    if (case_sensitive):
        conn.create_function("regexp", 2, py_regexp_csensitive, deterministic=True)
    else:
        conn.create_function("regexp", 2, py_regexp_cinsensitive, deterministic=True)
    
    curs = conn.cursor()

    # Find student with matching id
    curs.execute(f"SELECT * FROM submissions WHERE {id_type_colname} = ?", (id_value,))
    row_matches = curs.fetchall()

    if (len(row_matches) == 0):
        raise NameError("Could not find that student in the database.")

    # Print matches in that student's code
    print_matching_database_rows(pattern, row_matches, deliv_cols, deliv_files, case_sensitive, first_only, out_file, match_number_enabled=False, context_radius=context_radius)
    return



