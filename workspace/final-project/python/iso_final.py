from parse_commandline_args import parse_accelergy_commandline_args
from accelergy_wrapper import main_accelergy

if __name__ == "__main__":
    args = parse_accelergy_commandline_args()
    main_accelergy(args)