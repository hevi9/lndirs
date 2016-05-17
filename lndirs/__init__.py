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

ARGS = argparse.ArgumentParser()
ARGS.add_argument("--version",
                  action="version",
                  version="%(prog)s " + __version__,
                  )
ARGS.add_argument("-d", "--debug",
                  action="store_true",
                  help="set debug/development mode on"
                  )
ARGS.add_argument("-c", "--clean",
                  action="store_true",
                  help="clean target links"
                  )
ARGS.add_argument("-s", "--show",
                  action="store_true",
                  help="show links to be done (no action)"
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
    def __init__(self, target_root, target_path, source_path):
        self.target_root = target_root
        self.target_path = target_path  # relative to root
        self.source_path = source_path

    def __repr__(self):
        return "%r -> %r" % (self.target_path, self.source_path)

    @property
    def abspath(self):
        return j(self.target_root, self.target_path)

    def link(self):
        path = j(self.target_root, self.target_path)
        log.debug("mkdir %r", os.path.dirname(path))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            log.info("link %r -> %r", path, self.source_path)
            os.symlink(self.source_path, path)
        else:
            if os.path.islink(path):
                linkto = os.readlink(path)
                if linkto == self.source_path:
                    pass  # ok
                else:
                    log.info("target %r links to %r instead %r",
                             path, linkto, self.source_path)
            else:
                log.info("non-link file %r already exists",
                         path)

    def clean(self):
        path = j(self.target_root, self.target_path)
        if not os.path.exists(path):
            return
        if os.path.islink(path):
            linkto = os.readlink(path)
            if linkto == self.source_path:
                log.info("unlink %r", path)
                os.unlink(path)
            else:
                log.info("unlink %r -> %r, no source, not removed",
                         self.source_path, path)
        else:
            log.info("non-link file %r", self.target_path)

    def show(self):
        log.info("link %r -> %r", self.abspath, self.source_path)


def gather(target_root, source_roots):
    target_files = []
    for source_root in source_roots:
        for top, _, files in os.walk(source_root):
            for file in files:
                source_path = j(top, file)
                rpath = os.path.relpath(source_path, source_root)
                target_files.append(TargetFile(target_root, rpath, source_path))
    return target_files


def do_linking(target_files):
    for file in target_files:
        file.link()


def do_clean(target_files):
    clean_dirs = set()
    for file in target_files:
        file.clean()
        clean_dirs.add(os.path.dirname(file.abspath))
    for dir in clean_dirs:
        try:
            os.rmdir(dir)
            log.info("rmdir %r", dir)
        except OSError:
            pass  # cannot remove, ok


def do_show(target_files):
    for file in target_files:
        file.show()


def init_logging(args):
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def main(argv=sys.argv[1:]):
    args = ARGS.parse_args(argv)
    init_logging(args)
    target_files = gather(args.target, args.sources)
    if args.clean:
        do_clean(target_files)
    else:
        do_linking(target_files)
