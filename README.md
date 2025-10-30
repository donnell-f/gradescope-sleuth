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


    print file {-uin} {-file} [-nonums]
        Print the entirety of a deliverable file that a student submitted
        with syntax coloring and line numbers.
    Arguments:
        -file <file name>
            The name of the desired deliverable file.
        -uin <uin>
            The desired student's UIN.
        -nonums
            Don't print line numbers.
    

    print history {-uin | -email}
        Print the student's submission history in terms of points earned
        and lines changed per unit time.
    Arguments:
        -uin <uin>
            The desired student's UIN.
        -email <email> 
            The desired student's email.


    exit, quit, q
        Exits the program.



# Usage Notes

Usage notes:
- Only put one dash for arguments. The argument parser is not sophisticated enough to handle --args.
- Don't put quotes around argument params.


# How to Get Cookies for Network Settings

In order to access historical submissions, Gradescope Sleuth needs access to a valid Gradescope account. In order to circumvent issues with 2FA and institutional Gradescope accounts, Gradescope Sleuth stores a local copy of your session tokens (aka. session cookies) in config.json for authentication. Is this the most secure solution? No. But it gets the job done. Additionally, Gradescope Sleuth needs to know the course ID and assignment ID corresponding to the assignment you loaded in.

This section will explain how to copy your session tokens and other login info into Gradescope Sleuth.

Your session cookies should be visible in the browser whenever you visit Gradescope. One of the cookies is called "remember_me", the other is called "signed_token". Refer to the following screenshot for their location:

https://drive.google.com/file/d/1kD1zQo-xqvxvnQkpDGuX4YtwruW2HBqx/view?usp=sharing

After this, you will need to give Gradescope Sleuth a link to the "Review Grades" page for the assignment you loaded into Gradescope Sleuth (or really, any page that corresponds to that specific assignment).

https://drive.google.com/file/d/1UiDdOiiPv-NNP0QkgBSjzoI04qzthnjm/view?usp=sharing

After this, you should be done. Contact me if you have any problems.


