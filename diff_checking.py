import sqlite3
import os
import platform
from datetime import datetime, timedelta
import requests
from difflib import SequenceMatcher
from tabulate import tabulate

# Returns the counts of lines added, removed, and changed.
# This function was written by AI, but I reviewed it and it looks good to me.
def check_diffs(old, new, ignore_blank=True, ignore_ws=True):
    a = old
    b = new

    def norm(line):
        if ignore_ws:
            line = " ".join(line.split())
        return line

    if ignore_blank:
        a = [ln for ln in a if ln.strip() != ""]
        b = [ln for ln in b if ln.strip() != ""]

    a_n = list(map(norm, a))
    b_n = list(map(norm, b))

    sm = SequenceMatcher(a=a_n, b=b_n, autojunk=False)

    added = removed = changed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            added += (j2 - j1)
        elif tag == "delete":
            removed += (i2 - i1)
        elif tag == "replace":
            len_a = i2 - i1
            len_b = j2 - j1
            paired = min(len_a, len_b)   # lines truly “changed”
            changed += paired
            if len_b > len_a:
                added += (len_b - len_a)   # surplus insertions
            elif len_a > len_b:
                removed += (len_a - len_b) # surplus deletions

    return {"added": added, "removed": removed, "changed": changed}


