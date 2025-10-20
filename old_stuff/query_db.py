
import yaml
import sqlite3
import os
import platform

conn = sqlite3.connect('image_scaling.db')
conn.enable_load_extension(True)

# Load the SQLite3 regex extension depending on platform
if platform.system() == "Windows":
    conn.load_extension("./regexp.dll")
elif platform.system() == "Darwin":
    conn.load_extension("./regexp.dylib")
elif platform.system() == "Linux":
    conn.load_extension("./regexp.so")
else:
    print("ERROR: could not identify platform. Shutting down.")



