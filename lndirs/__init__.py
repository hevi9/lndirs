""" Link source directories files into one target directory. """

__all__ = (
    "main",
    "gather",
    "do_linking",
    "do_clean",
    "do_show"
)

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
    """ Target file link node. """

    def __init__(self, target_root, target_path, source_path):
        """
        target_root as path as str is root of the tree where files are linked.
        target_path as relative path as str is path from given source three to
        be linked into target tree. 
        source_path as relative or absosute path as str is link source file. """
        self.target_root = os.path.abspath(target_root)
        self.target_path = target_path  # relative to root or None XXX
        self.source_path = os.path.abspath(source_path)

    def __repr__(self):
        return "%r -> %r" % (self.target_path, self.source_path)

    @property
    def abspath(self):
        """ Target link absolute path. """
        return j(self.target_root, self.target_path)

    def link(self):
        """ Create target symlink to source file if needed.
        Creates missing parent directories as well. """
        path = j(self.target_root, self.target_path)
        self.make_dirs(os.path.dirname(path))
        if not os.path.lexists(path):
            log.info("link %r -> %r", path, self.source_path)
            os.symlink(self.source_path, path)
        else:
            if os.path.islink(path):
                linkto = os.readlink(path)
                if linkto == self.source_path:
                    pass
                    # log.debug("link %r -> %r already exists", path,
                    #          self.source_path)
                else:
                    log.info("target %r links to %r instead %r",
                             path, linkto, self.source_path)
            else:
                log.info("non-link file %r already exists",
                         path)

    def make_dirs(self, dir):
        """ Create missing parent directories. """
        try:
            if not os.path.exists(os.path.dirname(dir)):
                self.make_dirs(os.path.dirname(dir))
        except FileExistsError:
            pass
        try:
            os.mkdir(dir)
            log.debug("mkdir %r", dir)
        except FileExistsError:
            pass
        except OSError as ex:
            raise

    def clean(self):
        """ Remove target symlink file. Removes empty parent directories
        as well until given target tree root thas is not removed. """
        path = j(self.target_root, self.target_path)
        if not os.path.exists(path):
            return
        if os.path.islink(path):
            linkto = os.readlink(path)
            if linkto == self.source_path:
                log.info("unlink %r", path)
                os.unlink(path)
                self.clean_dir(os.path.dirname(path))
            else:
                log.info("unlink %r -> %r, no source, not removed",
                         self.source_path, path)
        else:
            log.info("non-link file %r", self.target_path)

    def clean_dir(self, dir):
        """ Clean directory and parent directories if empty. """
        if os.path.relpath(dir, self.target_root) == '.':
            return
        try:
            os.rmdir(dir)
            log.info("rmdir %r", dir)
        except OSError:
            return
        self.clean_dir(os.path.dirname(dir))

    def show(self):
        """ Show linking. """
        log.info("link %r -> %r", self.abspath, self.source_path)


def gather(target_root, source_roots):
    """ Gather source files and build target nodes. """

    target_files = []
    for source_root in source_roots:
        if not os.path.exists(source_root):
            raise FileNotFoundError(source_root)
        if not os.path.isdir(source_root):
            if os.path.isabs(source_root):
                target_files.append(
                    TargetFile(target_root, os.path.basename(source_root),
                               source_root))
            else:
                target_files.append(
                    TargetFile(target_root, source_root,
                               os.path.abspath(source_root)))
            continue
        for top, _, files in os.walk(source_root):
            for file in files:
                source_path = j(top, file)
                rpath = os.path.relpath(source_path, source_root)
                target_files.append(TargetFile(target_root, rpath, source_path))
    return target_files


def do_linking(target_files):
    """ Linking main operation. """
    for file in target_files:
        file.link()


def do_clean(target_files):
    """ Cleaning main operation. """
    for file in target_files:
        file.clean()


def do_show(target_files):
    """ Show links main operation. """
    for file in target_files:
        file.show()


def _init_logging(args):
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def main(argv=sys.argv[1:]):
    """ Main entry. argv as command line argument list. Return rc code: 0 = ok,
    others = failure. """
    args = ARGS.parse_args(argv)
    _init_logging(args)
    if os.path.exists(args.target) and not os.path.isdir(args.target):
        log.error("target tree %r is not directory", args.target)
        return 1
    try:
        target_files = gather(args.target, args.sources)
    except FileNotFoundError as ex:
        log.error("no file %r", str(ex))
        return 1
    if args.clean:
        do_clean(target_files)
    elif args.show:
        do_show(target_files)
    else:
        do_linking(target_files)
