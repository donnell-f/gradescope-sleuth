import sqlite3
import os
import platform
from datetime import datetime, timedelta
import re
import functools
from tabulate import tabulate

from .argument_parsing import ArgumentParser, ParsedArguments


############################################################################
#                           Notes for next time                            #
# - Add new `first_timestamp` column to db. Timestamp of first submission. #
# - Add new `last_timestamp` column to db. Timestamp of last submission.   #
# - Add new `attempts` column to db. Number of attempts.                   #
# - Use these new columns in here.                                         #
############################################################################
#                           Notes for future                               #
# - Move __main__() initialization (not database) into its own function.   #
#                                                                          #
############################################################################



def default_strftime(dt_object):
    return datetime.strptime(dt_object, "%Y-%m-%d %H:%M:%S") 

def sketchy_timestamps(parsed_args: ParsedArguments, due_date_input: str):
    hours_before = ParsedArguments.get_argument('-h')
    if (hours_before == False):
        raise NameError("Command `sketchy timestamps` needs -h arg.")
    else:
        hours_before = int(hours_before[0])
    
    due_date = datetime.strptime(due_date_input, "%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("submissions_db.db")
    curs = conn.cursor()

    dates_tuple = (
        default_strftime(due_date - timedelta(hours=hours_before)),
        default_strftime(due_date)
    )
    curs.execute("SELECT name, uin, email FROM submissions WHERE timestamp BETWEEN ? AND ?", dates_tuple)

    # Print the sketchy students found above
    sketchy_students = curs.fetchall()
    print(tabulate([("Name", "UIN", "E-Mail")] + curs.fetchall(), headers="firstrow", tablefmt="psql"))


def sketchy_attempts():
    pass

def sketchy_fast():
    pass

