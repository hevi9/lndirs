import lndirs
import pytest
import os
import shutil
import logging

log = logging.getLogger(__name__)
D = log.debug
logging.basicConfig(level=logging.DEBUG)
j = os.path.join
ROOT = os.path.dirname(__file__)
target = j(ROOT, "target")


@pytest.fixture
def target_tree(request):
    def fin():
        shutil.rmtree(target, ignore_errors=True)

    request.addfinalizer(fin)
    return target


@pytest.fixture(scope="session")
def src_base(request):
    class files:
        tree = j(ROOT, "src_base")
        file1_rel = j("dirA", "file1.txt")
        file1 = j(tree, file1_rel)

    return files


@pytest.fixture(scope="session")
def src_base2(request):
    class files:
        tree = j(ROOT, "src_base2")
        file1_rel = j("dirA", "file1.txt")
        file1 = j(tree, file1_rel)

    return files


def test_import():
    """ basic importing """
    lndirs.NAME
    lndirs.__version__


def test_version():
    """ version option """
    with pytest.raises(SystemExit):
        lndirs.main(["--version"])


def test_link(target_tree, src_base):
    """ tree base linking """
    lndirs.main(["-dt", target_tree, src_base.tree])
    assert os.readlink(j(target_tree, src_base.file1_rel)) == src_base.file1


def test_link_duplicate(target_tree, src_base):
    """ Test same duplicate source file """
    lndirs.main(["-dt", target_tree, src_base.tree, src_base.tree])
    assert os.readlink(j(target_tree, src_base.file1_rel)) == src_base.file1


def test_two_files_same_target(target_tree, src_base, src_base2):
    """ test linking two files to same target """
    lndirs.main(["-dt", target_tree, src_base.tree, src_base2.tree])
    assert os.readlink(j(target_tree, src_base.file1_rel)) == src_base.file1


def test_link_rel(target_tree):
    """ test linking for relative paths """
    source_tree = j(ROOT, "src_base")
    src_file = j(source_tree, "dirA", "file1.txt")
    tgt_file = j(target_tree, "dirA", "file1.txt")
    old_cwd = os.getcwd()
    os.chdir(source_tree)
    rel_target_tree = os.path.relpath(target_tree, source_tree)
    D("tree links %r -> . (%r)", rel_target_tree, os.getcwd())
    lndirs.main(["-dt", rel_target_tree, "."])
    assert os.readlink(tgt_file) == src_file
    os.chdir(old_cwd)


def test_link_file(target_tree, src_base):
    """ Link plain file to target tree """
    lndirs.main(["-dt", target_tree, src_base.file1])
    assert os.readlink(j(target_tree, os.path.basename(src_base.file1))) == src_base.file1


def test_link_target_file_fail(target_tree):
    """ Fail link to target if target is file """



def test_clean(target_tree):
    """ tree cleaning """
    lndirs.main(["-dt", target_tree, j(ROOT, "clean_tree")])
    lndirs.main(["-dct", target_tree, j(ROOT, "clean_tree")])
    assert len(os.listdir(target_tree)) == 0


def test_show(target_tree):
    """ show trees to be linked """
    lndirs.main(["-dst", target_tree,
                 j(ROOT, "linking_multitree")])
