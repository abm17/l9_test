import argparse


parser = argparse.ArgumentParser(description='Prints a list of instance-ids to STDOUT that can be accessed '
                                             'directly from a specific port, ip using a protocol')
parser.add_argument("instance_file_path",help="")
parser.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='an integer for the accumulator')
parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

args = parser.parse_args()
print(args.accumulate(args.integers))