import pkg_resources
import sys
import logging
import argparse

NAME = "lndirs"
try:
    __version__ = pkg_resources.get_distribution(NAME).version
except pkg_resources.DistributionNotFound:
    __version__ = "0.0.0"

log = logging.getLogger(NAME)
D = log.debug

ARGS = argparse.ArgumentParser()
ARGS.add_argument("--version",
                  action="version",
                  version="%(prog)s " + __version__,
                  )
ARGS.add_argument("-d", "--debug",
                  action="store_true",
                  help="set debug/development mode on"
                  )


def main(argv=sys.argv[1:]):
    args = ARGS.parse_args(argv)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
