import yaml
import sqlite3
import os
import platform

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

    return all_cpp_submitted.keys()



def initialize(submissions: dict):
    # Return a list of detected deliverable file names, use it to generate column headers
    deliverable_fnames = detect_deliverables(submissions)
    deliverable_colnames = [d.lower().replace(".", "_") for d in deliverable_fnames]
    deliverable_cols = [d + " TEXT" for d in deliverable_colnames]

    table_columns = ["submission_id INTEGER PRIMARY KEY"] + deliverable_cols + ["student_name TEXT NOT NULL", "uin INTEGER NOT NULL", "email TEXT", "timestamp TEXT", "score REAL"]

    conn = sqlite3.connect("submissions_db.db")

    # Create the submissions table
    conn.execute('''DROP TABLE IF EXISTS submissions''')     # Drop old version, if it exists
    conn.execute(f"CREATE TABLE IF NOT EXISTS submissions ({", ".join(table_columns)})")

    # Placehodler variables for reading files from submissions
    functions_cpp = None
    image_scaling_cpp = None

    # Add all submission metadata to database
    i = 0
    functions_cpp = ""
    image_scaling_cpp = ""
    for s in submissions:
        print(f"Uploading {i+1}/{len(submissions)} submssions to database. Current submission: {s}.")
        submission_id = int(s[s.index('_')+1:])

        # Gather file contents for submission
        # If file was unable to be read, just upload the default value (which is "") to database
        if os.path.isfile(f"{s}/functions.cpp"):
            with open(f"{s}/functions.cpp", "r") as f:
                functions_cpp = f.read()
        else:
            print(f"Submission {submission_id} does not have functions.cpp!")

        if os.path.isfile(f"{s}/image_scaling.cpp"):
            with open(f"{s}/image_scaling.cpp", "r") as f:
                image_scaling_cpp = f.read()
        else:
            print(f"Submission {submission_id} does not have image_scaling.cpp!")

        # Add stuff to db
        conn.execute(f'''INSERT INTO submissions(submission_id, functions_cpp, image_scaling_cpp, student_name, uin, email, timestamp, score) VALUES (?,?,?,?,?,?,?,?)''',
            (
                submission_id,
                functions_cpp,
                image_scaling_cpp,
                submissions[s][":submitters"][0][":name"],
                submissions[s][":submitters"][0][":sid"],
                submissions[s][":submitters"][0][":email"],
                str(submissions[s][":created_at"]),
                submissions[s][":score"]
            )
        )

        i += 1


    # Commit changes
    conn.commit()



