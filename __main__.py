import yaml
import sqlite3
import os
import platform

from .initialize import initialize

ymlloader = yaml.CSafeLoader

def main():
    # Print the logo
    with open("./logo.txt", "r") as f:
        print(f.read())

    # Test for config.json. If it doesn't exist, then the project hasn't been initialized, so initialize it.    
    submissions = None
    if (not os.path.isfile("./config.json")):
        print("Loading submission_metadata.yml, this could take a while...")
        with open("../submission_metadata.yml", "r") as f:
            submissions = yaml.load(f, Loader=ymlloader)
        initialize(submissions)
        


if __name__ == "__main__":
    main()
