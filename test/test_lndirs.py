import lndirs
import pytest
import os
import shutil

j = os.path.join
ROOT = os.path.dirname(__file__)
target = j(ROOT, "target")


def test_import():
    """ basic importing """
    lndirs.NAME
    lndirs.__version__


def test_version():
    """ version option """
    with pytest.raises(SystemExit):
        lndirs.main(["--version"])


def test_linking():
    """ tree linking """
    lndirs.main(
        ["-dt", j(ROOT, "target"),
         j(ROOT, "linking_multitree", "treeA"),
         j(ROOT, "linking_multitree", "treeB")]
    )
    shutil.rmtree(target)


def test_clean():
    """ tree cleaning """
    lndirs.main(["-dt", j(ROOT, "target"),
                 j(ROOT, "clean_tree")])
    lndirs.main(["-dct", j(ROOT, "target"),
                 j(ROOT, "clean_tree")])
    assert len(os.listdir(j(ROOT,"target"))) == 0


def test_show():
    """ show trees to be linked """
    lndirs.main(["-dst", j(ROOT, "target"),
                 j(ROOT, "linking_multitree")])