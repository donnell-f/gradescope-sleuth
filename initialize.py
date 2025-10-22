import yaml
import sqlite3
import os
import platform
from datetime import datetime
import json

ymlloader = yaml.CSafeLoader

def detect_deliverables(submissions: dict) -> list[str]:
    # Loop through submissions to find the most commonly submitted files
    # Any files that are submitted less than 80% of the time will be classified as non-deliverables
    # The others will be classified as deliverables
    all_cpp_submitted = {}
    count = 0
    for s in submissions:
        for fname in os.listdir(f"../{s}"):
            if ((fname in all_cpp_submitted.keys()) and (len(fname) >= 4)):
                all_cpp_submitted[fname] += 1
            else:
                all_cpp_submitted[fname] = 1
        count += 1

    # Select only C++ source / header files from all_cpp_submitted and convert occurrance count into occurrance proportion
    all_cpp_submitted = {k: all_cpp_submitted[k]/count for k in all_cpp_submitted if (k[-4:] == ".cpp" or k[-2:] == ".h")}
    # Select only the files whose occurrance proportion is >= 0.80
    all_cpp_submitted = {k: all_cpp_submitted[k] for k in all_cpp_submitted if (all_cpp_submitted[k] >= 0.80)}

    return list(all_cpp_submitted.keys())


def initialize():
    assignment_name = input("What is the name of this assignment?: ")
    assignment_name = assignment_name.strip()

    # Letting the user retry this one bc I could see this being a bit tricky.
    due_date = None
    while (due_date == None):
        due_date_input = input("When is the assignment due? Enter date in the form YYYY-MM-DD HH:MM: ")
        due_date_input = due_date_input.strip() + ":59"     # Add the last few seconds just in case that matters
        try:
            due_date = datetime.strptime(due_date_input, "%Y-%m-%d %H:%M:%S")
        except:
            print("Bad date input. Try again.")

    # Begin the initialization process by loading submission_metadata.yml
    submissions = None
    print("Loading submission_metadata.yml, this could take a while...")
    with open("../submission_metadata.yml", "r") as f:
        submissions = yaml.load(f, Loader=ymlloader)
    if (submissions == None):
        print("ERROR: failed to load submission_metadata.yml. Shutting down.")
        exit()

    # Return a list of detected deliverable file names, use it to generate column headers
    deliverable_fnames = detect_deliverables(submissions)
    deliverable_colnames = [d.lower().replace(".", "_") for d in deliverable_fnames]
    deliverable_cols = [d + " TEXT" for d in deliverable_colnames]

    table_colnames = ["submission_id"] + deliverable_colnames + ["student_name", "uin", "email", "last_timestamp", "first_timestamp", "final_score", "attempt_count"]
    table_columns = ["submission_id INTEGER PRIMARY KEY"] + deliverable_cols + ["student_name TEXT NOT NULL", "uin INTEGER NOT NULL", "email TEXT", "last_timestamp TEXT", "first_timestamp TEXT", "final_score REAL", "attempt_count INTEGER"]

    conn = sqlite3.connect("submissions_db.db")
    curs = conn.cursor()

    # Create the submissions table
    curs.execute('''DROP TABLE IF EXISTS submissions''')     # Drop old version, if it exists
    curs.execute(f"CREATE TABLE IF NOT EXISTS submissions ({", ".join(table_columns)})")

    # Dictionary with empty string as placeholder
    deliverables_dict = {cname: "" for cname in deliverable_colnames}
    # Add all submission metadata to database
    total_submissions_count = 0
    for s in submissions:
        print(f"Uploading {total_submissions_count+1}/{len(submissions)} submssions to database. Current submission: {s}.")
        submission_id = int(s[s.index('_')+1:])

        # Try reading all deliverables, if they exist
        # If they don't exist, they will just default to empty string
        for j in range(len(deliverable_fnames)):
            if (os.path.isfile(f"../{s}/{deliverable_fnames[j]}")):
                with open(f"../{s}/{deliverable_fnames[j]}", "r") as f:
                    deliverables_dict[deliverable_colnames[j]] = f.read()
            else:
                print(f">>> Submission {submission_id} does not have the file {deliverable_fnames[j]}. Skipping...")

        # Add stuff to db
        last_timestamp = submissions[s][":created_at"].strftime("%Y-%m-%d %H:%M:%S")    # yml autoconverts to datetime, so strftime is needed
        first_timestamp = None
        attempt_count = len(submissions[s][":history"]) + 1    # Last attempt is not included in :history
        if (attempt_count > 1):
            first_timestamp = submissions[s][":history"][-1][":created_at"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            first_timestamp = last_timestamp

        inserted_values = (submission_id,) + \
                        tuple(deliverables_dict[cn] for cn in deliverable_colnames) + \
                        (submissions[s][":submitters"][0][":name"],
                         submissions[s][":submitters"][0][":sid"],
                         submissions[s][":submitters"][0][":email"],
                         last_timestamp,
                         first_timestamp,
                         submissions[s][":score"],
                         attempt_count)
        question_marks = ",".join(['?' for _ in range(len(inserted_values))])
        curs.execute(f'''INSERT INTO submissions({", ".join(table_colnames)}) VALUES ({question_marks})''', inserted_values)

        total_submissions_count += 1


    # Write relevant config info to config.json
    try:
        config_dict = {}
        config_dict["assignment_name"] = assignment_name
        config_dict["due_date"] = due_date.strftime("%Y-%m-%d %H:%M:%S")
        config_dict["deliverables_column_file_mapping"] = {deliverable_colnames[i]: deliverable_fnames[i] for i in range(len(deliverable_colnames))}
        config_dict["submissions_count_total"] = total_submissions_count     # Not necessary, but perhaps good to know
        with open("config.json", "w") as fjson:
            json.dump(config_dict, fjson, indent=4)
    except:
        print("ERROR: could not write config info to config.json. Shutting down.")
        exit()

    # Commit changes and close
    conn.commit()
    curs.close()
    conn.close()
    


