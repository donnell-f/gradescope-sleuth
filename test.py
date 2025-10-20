
import yaml
import sqlite3
import os
import platform

ymlloader = yaml.CSafeLoader
submissions = None
print("Loading submission_metadata.yml, this could take a while...")
with open("../submission_metadata.yml", "r") as f:
    submissions = yaml.load(f, Loader=ymlloader)

# Loop through submissions to find the most commonly submitted files
# Any files that are submitted less than 80% of the time will be classified as non-deliverables
# The others will be classified as deliverables
all_cpp_submitted = {}
count = 0
for s in submissions:
    print("Processing a submission...")
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
# return all_cpp_submitted.keys()
    
