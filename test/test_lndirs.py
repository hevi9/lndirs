import lndirs
import pytest
import os


j = os.path.join
ROOT = os.path.dirname(__file__)


def test_00():
    """ basic importing """
    lndirs.NAME
    lndirs.__version__


def test_sync():
    lndirs.main(["-dt", j(ROOT, "target"), j(ROOT, "treeA"), j(ROOT, "treeB")])


def test_clean():
    pass


def test_version():
    with pytest.raises(SystemExit):
        lndirs.main(["--version"])

if __name__ == "__main__":
    test_sync()
