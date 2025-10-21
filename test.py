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
        print('-----------------------')
        print(file)
        print('-----------------------')
        print(pretty_file)
        print('-----------------------')

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
    
    def getPrettyLineWithContext(self, line_number, context_radius=1):
        
    
    def printAll(self):
        for ln in range(1, len(self.lines) + 1):
            print(self.getLine(ln))
    


def in_context_matches(pattern: str, file: str):
    ilm = IndexLineMapper(file)

    matches = re.finditer(pattern, file)
    for m in matches:
        print(m.start(), m.end())
        firstline = ilm.stringIndexToLineNum(m.start())
        print(firstline)
        lastline = ilm.stringIndexToLineNum(m.end() - 1)
        print(lastline)
        all_lines = [ilm.getPrettyLine(lnum) for lnum in range(firstline, lastline + 1)]
        # print(all_lines)
        print("\n".join(all_lines))
        print()




cpp_code = """
#include <iostream>
#include <sstream>
#include <fstream>
#include <cmath>
#include <string>
#include "functions.h"

using std::cout, std::endl, std::cin, std::string, std::stringstream;

int main() {
    // 2D vectors of pixels
    Image source_image;
    Image target_image;

    // declare variables
    string filename;
    unsigned int target_width = 0;
    unsigned int target_height = 0;

    // accept filename
    cout << "Input filename: ";
    cin >> filename;

    try {
        // attempt to load image
        source_image = load_image(filename);
        cout << "Detected image width: " << source_image.size() << endl;
        cout << "Detected image height: " << source_image.at(0).size() << endl;
    } catch (std::exception &ex) {
        cout << "Exception thrown: " << ex.what() << endl;
        return 1;  // exit with error
    }

    // accept target dimensions
    cout << "Input target width: ";
    cin >> target_width;
    cout << "Input target height: ";
    cin >> target_height;

}"""


## Working...
# all_newlines = "\n\n\na\n\n\n\n"
# ilm = IndexLineMapper(all_newlines)
# ln = ilm.stringIndexToLineNum(3)
# print(ilm.getLine(ln))
# print(ilm.getLine(ln+1))

# ilm = IndexLineMapper(cpp_code)
# # ilm.printDebug()
# ilm.printAll()


in_context_matches(r"try", cpp_code)

