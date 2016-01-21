import pkg_resources
import sys
import logging
import argparse
import os

j = os.path.join

NAME = "lndirs"
try:
    __version__ = pkg_resources.get_distribution(NAME).version
except pkg_resources.DistributionNotFound:
    __version__ = "0.0.0"

log = logging.getLogger(NAME)
D = log.debug


CFG = {
    "target": None,
    "sources": []
}

ARGS = argparse.ArgumentParser()
ARGS.add_argument("--version",
                  action="version",
                  version="%(prog)s " + __version__,
                  )
ARGS.add_argument("-d", "--debug",
                  action="store_true",
                  help="set debug/development mode on"
                  )
ARGS.add_argument("-t", "--target",
                  required=True,
                  help="target directory"
                  )
ARGS.add_argument("sources",
                  nargs="*",
                  metavar="SOURCE",
                  help="source directory"
                  )


class TargetFile:

    def __init__(self, target_path, source_path):
        self.target_path = target_path
        self.source_path = source_path

    def __repr__(self):
        return "%r -> %r" % (self.target_path, self.source_path)

    def link(self):
        os.makedirs(os.path.dirname(self.target_path), exist_ok=True)
        if not os.path.exists(self.target_path):
            os.symlink(self.source_path, self.target_path)
        else:
            if os.path.islink(self.target_path):
                linkto = os.readlink(self.target_path)
                if linkto == self.source_path:
                    pass  # ok
                else:
                    log.info("target %r links to %r instead %r",
                             self.target_path, linkto, self.source_path)
            else:
                log.info("non-link file %r already exists",
                         self.target_path)


def do_sync(target, sources):
    # D("%r %r", target, sources)
    target_files = []
    for source in sources:
        for top, _, files in os.walk(source):
            for file in files:
                source_path = j(top, file)
                rpath = os.path.relpath(source_path, source)
                target_files.append(TargetFile(j(target, rpath), source_path))
    # link files
    for file in target_files:
        file.link()


def main(argv=sys.argv[1:]):
    # set configuration
    cfg = CFG
    # process arguments
    args = ARGS.parse_args(argv)
    cfg["debug"] = args.debug
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    cfg["target"] = args.target
    cfg["sources"] = args.sources
    #
    do_sync(args.target, args.sources)
