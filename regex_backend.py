from datetime import datetime
import re
import itertools
from pygments.lexers import CppLexer
from pygments.formatters import TerminalFormatter
from pygments import highlight


class IndexLineMapper:
    lines =  []
    pretty_lines = []
    max_line_num = -1

    def __init__(self, file: str):
        lexer = CppLexer(stripnl=False)
        formatter = TerminalFormatter(style='default')
        pretty_file = highlight(file, lexer, formatter)

        if (file.strip() == ""):
            return

        self.lines = file.split('\n')
        self.pretty_lines = pretty_file.split('\n')

        # Line nums matches each line in the list with its line number
        line_nums = [i for i in range(1, len(self.lines) + 1)]

        # Accum line length denotes the length of each line *including* the \n
        # This means that accum_line_length[i] denotes the index of the first character of lines[i+1] in the file string
        # accum_line_length[-1] should be equal to len(file)
        accum_line_length = [len(l) for l in self.lines]
        accum_line_length = [a + 1 for a in accum_line_length]
        accum_line_length[-1] -= 1     # The last line, by definition, is not followed by a \n
        accum_line_length = list(itertools.accumulate(accum_line_length))

        self.lines = list(zip(self.lines, line_nums, accum_line_length))
        self.pretty_lines = list(zip(self.pretty_lines, line_nums, accum_line_length))

        # Setting this to make line numbering easier
        self.max_line_num = max(line_nums)


    
    def stringIndexToLineNum(self, strindex: int):
        lineIndex = None
        low = 0
        high = len(self.lines) - 1

        while (lineIndex == None):
            mid = low + (high - low) // 2
            last_line_offset = self.lines[mid - 1][2] if mid - 1 >= 0 else 0
            
            if (strindex < self.lines[mid][2] and strindex >= last_line_offset):
                lineIndex = mid
                break

            elif (strindex >= self.lines[mid][2]):
                low = mid + 1
                if (low > high or low > len(self.lines)):
                    lineIndex = -1
                    break
                else:
                    continue

            elif ( strindex < last_line_offset):
                high = mid - 1
                if (high < low or high < 0):
                    lineIndex = -1
                    break
                else:
                    continue

        
        if (lineIndex == -1):
            raise ValueError("Could not get line because string index is out of range.")

        # Return the line *number*
        return lineIndex + 1


    def getLine(self, line_number: int):
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        index = line_number - 1
        return self.lines[index][0]

    def getNumberedLine(self, line_number: int):
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        index = line_number - 1
        len_max_line_num = len(str(self.max_line_num))
        return f"{str(self.lines[index][1]).ljust(len_max_line_num)} │ {self.lines[index][0]}"

    def getPrettyLine(self, line_number: int):
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        index = line_number - 1
        len_max_line_num = len(str(self.max_line_num))
        return f"{str(self.pretty_lines[index][1]).ljust(len_max_line_num)} │ {self.pretty_lines[index][0]}"
    
    def getPrettyLineWithContext(self, line_number: int, context_radius=1):
        # Validity check
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        
        # Put together the lines
        index = line_number - 1
        output_line_indices = range(max(0, index - context_radius), min(index + context_radius + 1, len(self.pretty_lines)))
        output_lines = [self.getPrettyLine(oli + 1) for oli in output_line_indices]
        return "\n".join(output_lines)

    def getPrettyLinesWithContext(self, line_numbers: list[int], context_radius=1):
        if (len(line_numbers) == 1):
            return self.getPrettyLineWithContext(line_numbers[0], context_radius)

        # Validity check
        max_gap = 0
        increasing = True
        for i in range(len(line_numbers) - 1):
            increasing = increasing and (line_numbers[i+1] - line_numbers[i] > 0)
            max_gap = max(max_gap, abs(line_numbers[i+1] - line_numbers[i]))

        if (max_gap != 1 or increasing == False or line_numbers[0] < 1 or line_numbers[-1] > self.max_line_num):
            raise ValueError("Line numbers array is invalid.")
        
        # Put together the lines
        istart = line_numbers[0] - 1 - context_radius
        iend = line_numbers[-1] - 1 + context_radius
        output_line_indices = range(max(0, istart), min(iend + context_radius + 1, len(self.pretty_lines)))
        output_lines = [self.getPrettyLine(oli + 1) for oli in output_line_indices]
        return "\n".join(output_lines)

    def getNumberedLineWithContext(self, line_number: int, context_radius=1):
        # Validity check
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        
        # Put together the lines
        index = line_number - 1
        output_line_indices = range(max(0, index - context_radius), min(index + context_radius + 1, len(self.pretty_lines)))
        output_lines = [self.getNumberedLine(oli + 1) for oli in output_line_indices]
        return "\n".join(output_lines)

    def getNumberedLinesWithContext(self, line_numbers: list[int], context_radius=1):
        if (len(line_numbers) == 1):
            return self.getNumberedLineWithContext(line_numbers[0], context_radius)

        # Validity check
        max_gap = 0
        increasing = True
        for i in range(len(line_numbers) - 1):
            increasing = increasing and (line_numbers[i+1] - line_numbers[i] > 0)
            max_gap = max(max_gap, abs(line_numbers[i+1] - line_numbers[i]))

        if (max_gap != 1 or increasing == False or line_numbers[0] < 1 or line_numbers[-1] > self.max_line_num):
            raise ValueError("Line numbers array is invalid.")
        
        # Put together the lines
        istart = line_numbers[0] - 1 - context_radius
        iend = line_numbers[-1] - 1 + context_radius
        output_line_indices = range(max(0, istart), min(iend + context_radius + 1, len(self.pretty_lines)))
        output_lines = [self.getNumberedLine(oli + 1) for oli in output_line_indices]
        return "\n".join(output_lines)
        
    def getMaxLineNum(self):
        return self.max_line_num
    
    def printAll(self):
        for ln in range(1, len(self.lines) + 1):
            print(self.getLine(ln))
        



def get_in_context_matches(pattern: str, file: str, student_name: str, uin: str, email: str, file_name: str, match_number: int, case_sensitive: bool, pretty_printing: bool, first_only: bool):
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
    matches_header = f"Match #{match_number}  -  {UNDERLINE_START}{student_info}{UNDERLINE_END}  -  {UNDERLINE_START}{file_name}{UNDERLINE_END}"
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
            matches_with_context.append(ilm.getPrettyLinesWithContext(all_line_nums))
        else:
            matches_with_context.append(ilm.getNumberedLinesWithContext(all_line_nums))
    
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



