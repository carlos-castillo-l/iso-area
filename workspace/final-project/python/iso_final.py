from parse_commandline_args import parse_accelergy_commandline_args
from accelergy_wrapper import accelergy_wrapper

if __name__ == "__main__":
    args = parse_accelergy_commandline_args()
    accelergy_wrapper(args)