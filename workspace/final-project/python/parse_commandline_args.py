import argparse
import pyfiglet

def parse_accelergy_commandline_args():
    """
    Overrides Accelergy's original parse_commandline_args to add an argument for the iso-area design mode.
    """
    ascii_banner = pyfiglet.figlet_format("Accelergy")
    print(ascii_banner)
    """parse command line inputs"""
    parser = argparse.ArgumentParser(
        description='Accelergy is an architecture-level energy estimator for accelerator designs. Accelergy allows '
                    ' users to describe the architecture of a design with user-defined compound components and generates energy '
                    'estimations according to the workload-generated action counts.')
    parser.add_argument('-o', '--outdir', type=str, default='./',
                        help = 'Path to output directory that stores '
                               'the ERT and/or flattened_architecture and/or energy estimation. '
                               'Default is current directory.')
    parser.add_argument('-p', '--precision', type=int, default='5',
                        help= 'Number of decimal points for generated energy values. '
                              'Default is 3.')
    parser.add_argument('-v', '--verbose', type=int, default = 0,
                        help= 'If set to 1, Accelergy outputs the verbose version of the output files '
                              'Default is 0')
    parser.add_argument('-f', '--output_files',  nargs="*", type =str, default = ['all'],
                         help= 'list that contains the desired output files.'
                               ' Options include: ERT, ERT_summary, ART, ART_summary, energy_estimation, flattened_arch,'
                               ' and all (which refers to all possible outputs)')
    parser.add_argument('--oprefix', type =str, default = '',
                         help= 'prefix that will be added to the output files names.')
    parser.add_argument('files', nargs='*',
                        help= 'list of input files in arbitrary order.'
                              'Accelergy parses the top keys of the files to decide the type of input the file describes, '
                                                                    'e.g., architecture description, '
                                                                          'compound component class descriptions, etc. '
                        )
    parser.add_argument('--iso_area', type =int, default = 0,
                         help= 'If set to 1, use Accelergy to find iso-area designs on the given architecture'
                               'Default is 0')

    return parser.parse_args()