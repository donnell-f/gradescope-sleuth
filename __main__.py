MISSING_PACKAGES = False

try:
    import yaml
except:
    print("The `PyYAML` package is missing. Please run `pip install PyYAML`.")
    MISSING_PACKAGES = True
try:
    import prompt_toolkit
except:
    print("The `prompt_toolkit` package is missing. Please run `pip install prompt_toolkit`.")
    MISSING_PACKAGES = True
try:
    import pygments
except:
    print("The `Pygments` package is missing. Please run `pip install Pygments`.")
    MISSING_PACKAGES = True
try:
    import tabulate
except:
    print("The `tabulate` package is missing. Please run `pip install tabulate`.")
    MISSING_PACKAGES = True

if (MISSING_PACKAGES):
    exit()

import sqlite3
import os
import platform
import json
import datetime
from prompt_toolkit.formatted_text import ANSI

from .initialize_program import initialize_all
from .regex_commands import regex_all, regex_one
from .argument_parsing import ArgumentParser, is_command
from .sketchy_commands import sketchy_timestamps, sketchy_attempts
from .make_parsers import make_parsers
from .print_commands import print_student

CYAN = '\033[36m'
RESET = '\033[0m'

def main():
    init_values = initialize_all()
    assn_name = init_values['assn_name']
    config_dict = init_values['config_dict']
    prompt_session = init_values['prompt_session']

    parsers = make_parsers()
    regex_all_parser = parsers['regex all']
    regex_one_parser = parsers['regex one']
    sketchy_timestamps_parser = parsers['sketchy timestamps']
    sketchy_attempts_parser = parsers['sketchy attempts']
    print_parser = parsers['print']


    while (True):
        raw_input = None
        try:
            # Provide the prompt text here so prompt_toolkit renders it correctly.
            raw_input = prompt_session.prompt(ANSI(f"({CYAN}{assn_name}{RESET}) => "))
            raw_input = raw_input.strip()
        except EOFError as e:
            print(f"ERROR: {e}")
            break
        except KeyboardInterrupt as e:
            break

        try:
            # Handle blank input
            if (raw_input == ""):
                continue

            # Handle `regex all` command
            elif (is_command(raw_input, "regex all")):
                regex_all(
                    config_dict['deliverables_column_file_mapping'],
                    regex_all_parser.parse_args(raw_input)
                )
                continue

            # Handle `regex one` command
            elif (is_command(raw_input, "regex one")):
                regex_one(
                    config_dict['deliverables_column_file_mapping'],
                    regex_one_parser.parse_args(raw_input)
                )
                continue
            
            # Handle `sketchy timestamps` command
            elif (is_command(raw_input, "sketchy timestamps")):
                sketchy_timestamps(
                    config_dict['due_date'],
                    config_dict['late_due_date'],
                    sketchy_timestamps_parser.parse_args(raw_input)
                )
                continue

            # Handle `sketchy attempts` command
            elif (is_command(raw_input, "sketchy attempts")):
                sketchy_attempts(
                    config_dict['due_date'],
                    sketchy_attempts_parser.parse_args(raw_input)
                )
                continue

            # Handle `print`
            elif (is_command(raw_input, "print")):
                print_student(config_dict["deliverables_column_file_mapping"], print_parser.parse_args(raw_input))
                continue

            # Handle `reset` command
            elif (raw_input == "reset"):
                confirm_reset = input("Really reset database? (yes/no): ")
                if (confirm_reset.lower() != "yes"):
                    print("Reset interrupted by used. Nothing was changed.")
                    continue
                else:
                    os.remove("config.json")
                    print("Reset complete. Reopen the app for changes to take effect.")
                    break     # Note: break or exit()?

            elif (raw_input == "help"):
                with open("./help.txt", "r") as helpf:
                    print(helpf.read())

            # Handle `quit` and `exit` commands
            elif (raw_input == "quit" or raw_input == "exit" or raw_input == "q"):
                break

            else:
                print("ERROR: invalid command. Try again.")

        except NameError as e:
            # Catch NameErrors, since I am using them to indicate that something non-serious went wrong (i.e. user put a bad value in for an argument.)
            print(f"ERROR: {e}")
            print("Try again.")



if __name__ == "__main__":
    main()
