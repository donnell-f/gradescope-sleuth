from .argument_parsing import ArgumentParser

def make_parsers():
    # `regex all` parser
    regex_all_parser = ArgumentParser("regex all")
    regex_all_parser.add_argument('-case', 0)
    regex_all_parser.add_argument('-v', 0)
    regex_all_parser.add_argument('-f', 0)
    regex_all_parser.add_argument('-outf', 1)
    regex_all_parser.add_argument('-simple', 0)
    regex_all_parser.add_argument('-crad', 1)

    # `regex one` parser
    regex_one_parser = ArgumentParser("regex one")
    regex_one_parser.add_argument('-uin', 1)
    regex_one_parser.add_argument('-email', 1)
    regex_one_parser.add_argument('-case', 0)
    regex_one_parser.add_argument('-f', 0)
    regex_one_parser.add_argument('-outf', 1)
    regex_one_parser.add_argument('-crad', 1)

    # `sketchy timestamps` parser
    sketchy_timestamps_parser = ArgumentParser("sketchy timestamps")
    sketchy_timestamps_parser.add_argument("-h", 1)
    sketchy_timestamps_parser.add_argument("-late", 0)
    sketchy_timestamps_parser.add_argument('-simple', 0)

    # `sketchy attempts` parser
    sketchy_attempts_parser = ArgumentParser("sketchy attempts")
    sketchy_attempts_parser.add_argument('-natt', 1)
    sketchy_attempts_parser.add_argument('-minsc', 1)
    sketchy_attempts_parser.add_argument('-nolate', 0)
    sketchy_attempts_parser.add_argument('-simple', 0)

    # `print` parser
    print_parser = ArgumentParser('print')
    print_parser.add_argument('-uin', 1)
    print_parser.add_argument('-file', 1)
    print_parser.add_argument('-nonums', 0)

    return {
        'regex all': regex_all_parser,
        'regex one': regex_one_parser,
        'sketchy timestamps': sketchy_timestamps_parser,
        'sketchy attempts': sketchy_attempts_parser,
        'print': print_parser
    }


