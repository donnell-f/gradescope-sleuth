# Check if `raw_input` is an instance of `cmd`
def is_command(raw_input: str, cmd: str):
    return (len(raw_input) >= len(cmd) and raw_input[0:len(cmd)] == cmd)

class ArgumentParser:
    arguments = {}
    output_args = None
    cmd_name = None
    args_parsed = False

    def __init__(self, cmd_name):
        self.cmd_name = cmd_name

    # @param arg: e.g. '-f', '-csens', '-v'
    # @param nparams: the number of parameters the argument takes (0 for binary args)
    def add_argument(self, arg: str, nparams: int):
        self.arguments[arg.strip()] = nparams
    
    # @param arg: the arg whose value you want to get
    def get_argument(self, arg):
        if (self.args_parsed):
            return self.output_args[arg]
        else:
            raise KeyError("You must parse the args before you can read their values.")

    # Get the leftovers (mainly for regex)
    def get_remainder(self):
        if (self.args_parsed):
            return self.output_args['__remainder__']
        else:
            raise KeyError("You must parse the args before you can read their values.")
    
    # Self explanatory
    def get_cmd_name(self):
        return self.cmd_name

    # Self explanatory
    def print_args(self):
        if (self.args_parsed):
            print(self.output_args)
        else:
            raise KeyError("You must parse the args before you can read their values.")

    # @param raw_cmd_input: the raw input that it gets from main loop
    # @returns output_args: output args dictionary will show true for binary args that are present,
    #                       false for any arg that is not present, and will return a list of
    #                       parameters for args that take parameters. Also, it will have an entry
    #                       called "__remainder__" which denotes anything remaining at the end of
    #                       the command not accounted for by other args (this is just for `regex`).
    #                       Not supporting variable length args right now.
    def parse_args(self, raw_cmd_input) -> dict:
        output_args = {}
        cmd_split = raw_cmd_input.split(' ')

        # Keeps track of which parts of the command have been "used" or "consumed". Helpful for finding __remainder__.
        args_consumption_map = [False for _ in range(len(cmd_split))]    
        for i in range(len(self.name.split(' '))):
            args_consumption_map[i] = True
        
        # Handle non-present args
        for a in self.arguments:
            if (a not in cmd_split):
                output_args[a] = False
        
        # Handle present binary args
        for a in self.arguments:
            if (self.arguments[a] == 0 and (a in cmd_split)):
                args_consumption_map[cmd_split.index(a)] = True
                output_args[a] = True

        # Handle present parameter args
        for a in self.arguments:
            if (self.arguments[a] > 0 and (a in cmd_split)):
                if (cmd_split.index(a) + self.arguments[a] < len(cmd_split)):
                    # Handle parameter arg declaration
                    startpos = cmd_split.index(a)
                    args_consumption_map[startpos] = True
                    output_args[a] = []
                    # Handle the arg's parameters
                    for offset in range(1, len(self.arguments[a]) + 1):
                        args_consumption_map[startpos + offset] = True
                        output_args[a].append(cmd_split[startpos + offset])
                else:
                    raise ValueError(f"Not enough parameters for argument taking {self.arguments[a]} parameters.")
        
        # Verify that the list is made up of exactly two contiguous secitons of Falses and Trues
        # This will make it easy to detect too many args
        # It will also make it easy to find the remainder
        last_consumed_idx = 0 
        while (last_consumed_idx < len(args_consumption_map) and args_consumption_map[last_consumed_idx] != False):
            last_consumed_idx += 1
        consumed_remainder = args_consumption_map[last_consumed_idx:]
        if (True in consumed_remainder):
            raise ValueError("Too many args in command.")

        # Finally set the __remainder__
        output_args["__remainder__"] = args_consumption_map[last_consumed_idx:]

        # Save results to as member
        self.output_args = output_args
        self.args_parsed = True







