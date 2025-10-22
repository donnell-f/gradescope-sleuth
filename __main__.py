import yaml
import sqlite3
import os
import platform
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import ANSI

from .initialize import initialize
from .regex_commands import regex_all, regex_one
from .argument_parsing import ArgumentParser, is_command

CYAN = '\033[36m'
RESET = '\033[0m'

def main():
    # Change into gradescope_sleuth folder since we will be running this as a module
    os.chdir("./gradescope_sleuth")

    # Print the logo
    with open("./logo.txt", "r") as f:
        print(f.read())

    # Test for config.json. If it doesn't exist, then the project hasn't been initialized, so initialize it.    
    submissions = None
    if (not os.path.isfile("./config.json")):
        init_input = input("No config.json file detected. Run first time init? (y/n): ")
        if (init_input.lower() != "y"):
            print("Alright. See you later.")
            exit()
        print("Initializing program...")
        initialize()
        print("Initialization complete!")
    
    # Load data from config.json
    config_dict = None
    try:
        with open("config.json", "r") as fjson:
            config_dict = json.load(fjson)
    except:
        print("ERROR: could not load config.json! Shutting down...")
        exit()
    assn_name = config_dict['assignment_name']

    # # Make parsers
    # `regex all` parser
    regex_all_argparser = ArgumentParser("regex all")
    regex_all_argparser.add_argument('-case', 0)
    regex_all_argparser.add_argument('-v', 0)
    regex_all_argparser.add_argument('-f', 0)
    regex_all_argparser.add_argument('-outf', 1)
    # `regex one` parser
    regex_uin_argparser = ArgumentParser("regex one")
    regex_all_argparser.add_argument('-uin', 1)
    regex_all_argparser.add_argument('-email', 1)
    regex_all_argparser.add_argument('-case', 0)
    regex_all_argparser.add_argument('-f', 0)
    regex_all_argparser.add_argument('-outf', 1)

    # Create command history file if not exists
    if (not os.path.isfile("./command_history.log")):
        with open("./command_history.log", "a") as histf:
            pass

    # Create the prompt session
    session = PromptSession(history=FileHistory("command_history.log"))

    while (True):
        raw_input = None
        try:
            # Provide the prompt text here so prompt_toolkit renders it correctly.
            raw_input = session.prompt(ANSI(f"({CYAN}{assn_name}{RESET}) => "))
            raw_input = raw_input.strip()
        except EOFError as e:
            print(f"ERROR: {e}")
            break
        except KeyboardInterrupt as e:
            break
        
        # raw_input = input(f"(\x1b[36m{assn_name}\x1b[0m) => ")
        # raw_input = raw_input.strip()     # NOTE: is this ok?

        # # try:
        # Handle blank input
        if (raw_input == ""):
            continue

        # Handle `regex all` command
        elif (is_command(raw_input, "regex all")):
            regex_all(
                config_dict['deliverables_column_file_mapping'],
                regex_all_argparser.parse_args(raw_input)
            )
            continue

        elif (is_command(raw_input, "regex one")):
            try:
                regex_one(
                    config_dict['deliverables_column_file_mapping'],
                    regex_uin_argparser.parse_args(raw_input)
                )
            except NameError as e:
                print(f"ERROR: {e}")
                print("Try again.")
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

        # Handle `quit` and `exit` commands
        elif (raw_input == "quit" or raw_input == "exit" or raw_input == "q"):
            break

        else:
            print("ERROR: invalid command. Try again.")

        # # except Exception as e:
        # #     print(f"ERROR: {e}")
        # #     continue



if __name__ == "__main__":
    main()
