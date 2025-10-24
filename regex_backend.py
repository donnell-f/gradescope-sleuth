from datetime import datetime
import re
import itertools
from pygments.lexers import CppLexer
from pygments.formatters import TerminalFormatter
from pygments import highlight
import functools

from .index_line_mapper import IndexLineMapper

def get_in_context_matches(pattern: str, file: str, student_name: str, uin: str, email: str, file_name: str, match_number_enabled: bool, match_number: int, case_sensitive: bool, pretty_printing: bool, first_only: bool, context_radius: int):
    output_string = ""

    UNDERLINE_START = None
    UNDERLINE_END = None
    if pretty_printing:
        UNDERLINE_START = "\033[4m"
        UNDERLINE_END = "\033[0m"
    else:
        UNDERLINE_START = ""
        UNDERLINE_END = ""

    ilm = IndexLineMapper(file)
    student_info = f"{student_name}, {uin}, {email}"
    matches_header = None
    if match_number_enabled:
        matches_header = f"Match #{match_number}  -  {UNDERLINE_START}{student_info}{UNDERLINE_END}  -  {UNDERLINE_START}{file_name}{UNDERLINE_END}"
    else:
        matches_header = f"{UNDERLINE_START}{student_info}{UNDERLINE_END}  -  {UNDERLINE_START}{file_name}{UNDERLINE_END}"
    line_ext_length = len(matches_header) + len(str(ilm.getMaxLineNum())) + 3 - len(f"{UNDERLINE_START}{UNDERLINE_END}{UNDERLINE_START}{UNDERLINE_END}")


    # Save all matches with context to matches_with_context
    matches = None
    if case_sensitive:
        matches = re.finditer(pattern, file)
    else:
        matches = re.finditer(pattern, file, re.IGNORECASE)

    matches_with_context = []
    for m in matches:
        firstline = ilm.stringIndexToLineNum(m.start())
        lastline = ilm.stringIndexToLineNum(m.end() - 1)
        all_line_nums = [lnum for lnum in range(firstline, lastline + 1)]
        if pretty_printing:
            matches_with_context.append(ilm.getPrettyLinesWithContext(all_line_nums, context_radius=context_radius))
        else:
            matches_with_context.append(ilm.getNumberedLinesWithContext(all_line_nums, context_radius=context_radius))
    
    # Only print header if there were no matches
    if (matches_with_context == []):
        output_string += (len(str(ilm.getMaxLineNum()))*'─' + "───" + line_ext_length*'─') + "\n"
        output_string += (3*' ' + matches_header) + "\n"
        output_string += (len(str(ilm.getMaxLineNum()))*'─' + "───" + line_ext_length*'─') + "\n"
        return output_string

    # Remain only the first element in matches with context if `-f` flag is passed
    if (first_only):
        matches_with_context = matches_with_context[0:1]
    
    # Print student info header
    output_string += (len(str(ilm.getMaxLineNum()))*'─' + "───" + line_ext_length*'─') + "\n"
    output_string += (3*' ' + matches_header) + "\n"
    output_string += (len(str(ilm.getMaxLineNum()))*'─' + "─┬─" + line_ext_length*'─') + "\n"

    # Print the matches stored with matches_with_context
    output_string += (('\n' + len(str(ilm.getMaxLineNum()))*'─' + "─┼─" + line_ext_length*'─' + "\n").join(matches_with_context)) + "\n"
    output_string += (len(str(ilm.getMaxLineNum()))*'─' + "─┴─" + line_ext_length*'─') + "\n"

    return output_string



# Added LRU cache for speed
@functools.lru_cache(maxsize=256)
def _compile_cinsensitive(pat):
    return re.compile(pat, re.IGNORECASE)
@functools.lru_cache(maxsize=256)
def _compile_csensitive(pat):
    return re.compile(pat)


# Define two implementations of the regex function: one for case insensitive, and one for case sensitive
def py_regexp_cinsensitive(pattern, value):
    if pattern is None or value is None:
        return 0
    try:
        return 1 if _compile_cinsensitive(pattern).search(str(value)) else 0
    except re.error:
        return 0
def py_regexp_csensitive(pattern, value):
    if pattern is None or value is None:
        return 0
    try:
        return 1 if _compile_csensitive(pattern).search(str(value)) else 0
    except re.error:
        return 0

