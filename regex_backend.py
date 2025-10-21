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
        lexer = CppLexer()
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
        accum_line_length = list(itertools.accumulate(line_nums))
        accum_line_length = [accum_line_length[i] + len(self.lines[i]) for i in range(len(accum_line_length))]

        self.lines = zip(self.lines, line_nums, accum_line_length)
        self.pretty_lines = zip(self.pretty_lines, line_nums, accum_line_length)

        # Setting this to make line numbering easier
        max_line_num = max(line_nums)
    
    def stringIndexToLineNum(self, strindex: int):
        lineIndex = None
        low = 0
        high = len(self.lines) - 1
        while (lineIndex == None):
            mid = low + (high - low) // 2
            if (strindex < self.lines[mid][2]):
                lineIndex = mid
                break
            elif (strindex >= self.lines[mid][2]):
                low = mid + 1
                if (low > high or low > len(self.lines)):
                    lineIndex = -1
                    break
                else:
                    continue
            elif ( strindex < self.lines[mid][2] - len(self.lines[mid][0])):
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
        return f"{str(self.lines[index][1]):<len_max_line_num} │ {self.lines[index][0]}"

    def getPrettyLine(self, line_number: int):
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        index = line_number - 1
        len_max_line_num = len(str(self.max_line_num))
        return f"{str(self.pretty_lines[index][1]):<len_max_line_num} │ {self.pretty_lines[index][0]}"
        



def in_context_matches(pattern: str, file: str):
    ilm = IndexLineMapper(file)

    matches = re.findall(pattern, file)
    for m in matches:
        firstline = ilm.stringIndexToLineNum(m.start())
        lastline = ilm.stringIndexToLineNum(m.end() - 1)
        all_lines = [ilm.getPrettyLine(lnum) for lnum in range(firstline, lastline + 1)]
        print("\n".join(all_lines))
        print()



