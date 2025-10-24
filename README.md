# Gradescope Sleuth

Welcome to Gradescope Sleuth! This tool was designed to make it easier to look for plagiarized and AI-generated code in Gradescope submissions. Below are a list of commands the program supports.

Commands (from help message):

    regex all [-v] [-f] [-case] [-simple] [-outf] <expression>
        By default, prints a list of all students with code submissions that
        contain a match for <expression>. When -v is passed, the command will
        print the actual content of the matches as well.
    Arguments:
        -v
            A very powerful argument. If you pass in this argument, it will
            print the lines that all matches occur on as well as one line
            above and one line below it, for context.
        -f
            If you have already passed -v, -f makes it so that `regex all`
            will only print the first in-context match.
        -case
            Runs <expression> in case-sensitive mode.
        -simple
            Prints matching submissions as a simple list of names and UINs.
            Cannot be used with -v.
        -outf <filename>
            Writes output to <filename> in submissions directory. Note: don't
            put quotes around the file name or specify a path. That is not
            supported yet.
        -crad
            Set the context radius for in-context matches (i.e. how many
            lines to print above and below the match).


    regex one {-uin | -email} [-case] [-f] [-outf] <expression>
        Print all in-context matches for a single person's code.
    Arguments:
        -uin <uin>
            Use this to identify the student by their UIN.
        -email <email>
            Use this to identify the student by their email.
        -f
            Only return the first in-context match.
        -outf
            Writes output to <filename> in submissions directory. Note: don't
            put quotes around the file name or specify a path. That is not
            supported yet.
        -crad
            Set the context radius for in-context matches (i.e. how many
            lines to print above and below the match).


    sketchy timestamps {-h} [-late] [-simple]
        Print a list of all students whose first submission was submitted
        <hours before> hours before the deadline. If -late is passed, this
        analysis will be run on the late deadline.
    Arguments:
        -h <hours before>
            The amount of hours before the deadline to filter by.
        -late
            Use late deadline instead of the normal deadline.
        -simple
            Prints the returned submissions as a simple list of names and
            UINs.


    sketchy attempts {-natt} {-minsc} [-nolate] [-simple]
        Print a list of all students that got a score of <min score> after
        only <attempt num> attempts.
    Arguments:
        -natt <attempt num>
            Number of attempts to filter by.
        -minsc <min score>
            Minimum score to filter by.
        -nolate
            Filters out all late submissions from output if passed. This can
            be useful because late submissions often have bad/weird metadata.
        -simple
            Prints the returned submissions as a simple list of names and
            UINs.


    print {-uin} {-file} [-nonums]
        Print the entirety of a deliverable file that a student submitted
        with syntax coloring and line numbers.
    Arguments:
        -file <file name>
            The name of the desired deliverable file.
        -uin <uin>
            The desired student's UIN.
        -nonums
            Don't print line numbers.


    exit, quit, q
        Exits the program.


Usage notes:
- Only put one dash for arguments. The argument parser is not sophisticated enough to handle --args.
- Don't put quotes around arguments.



