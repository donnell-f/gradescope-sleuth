import yaml
import sqlite3
import os
import platform

ymlloader = yaml.CSafeLoader

confirmation = input("This script will delete the current database (if it exists) and regenerate it. Do you really want to do that? (y/n): ")
if (confirmation != 'y'):
    exit()

print("Loading submission info from submission_metadata.yml... This might take a long time...")
submissions = None
with open("submission_metadata.yml", "r") as f:
    submissions = yaml.load(f, Loader=ymlloader)

conn = sqlite3.connect("image_scaling.db")

# Create the submissions table
conn.execute('''DROP TABLE IF EXISTS submissions''')     # Drop old version, if it exists
conn.execute('''
CREATE TABLE IF NOT EXISTS submissions (
    submission_id INTEGER PRIMARY KEY,
    functions_cpp TEXT,
    image_scaling_cpp TEXT,
    student_name TEXT NOT NULL,
    uin INTEGER NOT NULL,
    email TEXT,
    timestamp TEXT,
    score REAL
)
''')

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
