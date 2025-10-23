import sqlite3
import os
import platform
from datetime import datetime, timedelta
import re
import functools
from tabulate import tabulate

from .argument_parsing import ArgumentParser, ParsedArguments

def get_hour_difference(start_date_input, end_date_input):
    start_date = start_date_input
    end_date = end_date_input
    if (type(start_date_input) == str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    if (type(end_date_input) == str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

    if (start_date > end_date):
        raise ValueError("End date must be later than start date.")
    
    return (end_date - start_date).total_seconds() / 3600



def sketchy_timestamps(due_date_input: str, late_due_date_input: str, parsed_args: ParsedArguments):
    hours_before = parsed_args.get_argument('-h')
    use_late_dd = parsed_args.get_argument('-late')
    simple_output = parsed_args.get_argument('-simple')
    if (hours_before == False):
        raise NameError("Command `sketchy timestamps` needs -h arg.")
    else:
        hours_before = int(hours_before[0])

    chosen_due_date = None
    if (use_late_dd == True):
        chosen_due_date = datetime.strptime(late_due_date_input, "%Y-%m-%d %H:%M:%S")
    else:
        chosen_due_date = datetime.strptime(due_date_input, "%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("submissions_db.db")
    curs = conn.cursor()

    dates_tuple = (
        datetime.strftime(chosen_due_date - timedelta(hours=hours_before), "%Y-%m-%d %H:%M:%S"),
        datetime.strftime(chosen_due_date, "%Y-%m-%d %H:%M:%S")
    )
    curs.execute("SELECT student_name, uin, email, first_timestamp FROM submissions WHERE first_timestamp BETWEEN ? AND ?", dates_tuple)

    # Print the sketchy students found above
    sketchy_students = curs.fetchall()
    sketchy_students = [(ss[0], ss[1], ss[2], round(get_hour_difference(ss[3], chosen_due_date), 2)) for ss in sketchy_students]
    print(f"{len(sketchy_students)} matches.")
    if (not simple_output):
        print(tabulate([("Name", "UIN", "E-Mail", "Hrs Before Deadline")] + sketchy_students, headers="firstrow", tablefmt="psql"))
    else:
        for ss in sketchy_students:
            print(f"{ss[0]}, {ss[1]}")


def sketchy_attempts(due_date_input: str, parsed_args: ParsedArguments):
    attempt_count = parsed_args.get_argument('-natt')
    min_score = parsed_args.get_argument('-minsc')
    no_late_submissions = parsed_args.get_argument('-nolate')
    simple_output = parsed_args.get_argument('-simple')
    if (attempt_count == False):
        raise ValueError("You must specify a maximum number of attempts with -natt.")
    else:
        attempt_count = int(attempt_count[0])
    if (min_score == False):
        raise ValueError("You must specify a minimum score with -minsc.")
    else:
        min_score = float(min_score[0])

    # due_date = datetime.strptime(due_date_input, "%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect("submissions_db.db")
    curs = conn.cursor()

    if no_late_submissions:
        curs.execute("SELECT student_name, uin, email, attempt_count FROM submissions WHERE attempt_count <= ? AND final_score >= ? AND last_timestamp < ?", (attempt_count, min_score, due_date_input))
    else:
        curs.execute("SELECT student_name, uin, email, attempt_count FROM submissions WHERE attempt_count <= ? AND final_score >= ?", (attempt_count, min_score))

    # Print the sketchy students found above
    sketchy_students = curs.fetchall()
    print(f"{len(sketchy_students)} matches.")
    if (not simple_output):
        print(tabulate([("Name", "UIN", "E-Mail", "Attempt Count")] + sketchy_students, headers="firstrow", tablefmt="psql"))
    else:
        for ss in sketchy_students:
            print(f"{ss[0]}, {ss[1]}")


