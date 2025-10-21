import yaml
import sqlite3
import os
import platform
import json

from .initialize import initialize
from .regex_commands import regex_all
from .argument_parsing import ArgumentParser, is_command


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
    regex_all_argparser.add_argument('-csens', 0)
    regex_all_argparser.add_argument('-v', 0)
    regex_all_argparser.add_argument('-f', 0)

    # Run the main loop to prompt user
    while (True):
        raw_input = input(f"(\x1b[36m{assn_name}\x1b[0m) => ")
        raw_input = raw_input.strip()     # NOTE: is this ok?

        # # try:
        # Handle blank input
        if (raw_input == ""):
            continue

        # Handle `regex all` command
        if (is_command(raw_input, "regex all")):
            regex_all(config_dict['deliverables_column_file_mapping'],
                        regex_all_argparser.parse_args(raw_input))
            continue

        # Handle `reset` command
        if (raw_input == "reset"):
            confirm_reset = input("Really reset database? (yes/no): ")
            if (confirm_reset.lower() != "yes"):
                print("Reset interrupted by used. Nothing was changed.")
                continue
            else:
                os.remove("config.json")
                print("Reset complete. Reopen the app for changes to take effect.")
                break     # Note: break or exit()?

        # Handle `quit` and `exit` commands
        if (raw_input == "quit" or raw_input == "exit"):
            break


        # # except Exception as e:
        # #     print(f"ERROR: {e}")
        # #     continue



if __name__ == "__main__":
    main()
