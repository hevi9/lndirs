import lndirs
import pytest
import os
import shutil
import logging

log = logging.getLogger(__name__)
D = log.debug

j = os.path.join
ROOT = os.path.dirname(__file__)
target = j(ROOT, "target")


@pytest.fixture
def target_tree(request):
    print("FIX enter target_tree")

    def fin():
        print("FIX leave rmtree %r", target)
        shutil.rmtree(target, ignore_errors=True)

    request.addfinalizer(fin)
    return target


def test_test(target_tree):
    print(target_tree)


def test_import():
    """ basic importing """
    lndirs.NAME
    lndirs.__version__


def test_version():
    """ version option """
    with pytest.raises(SystemExit):
        lndirs.main(["--version"])


def test_linking(target_tree):
    """ tree linking """
    lndirs.main(
        ["-dt", target_tree,
         j(ROOT, "linking_multitree", "treeA"),
         j(ROOT, "linking_multitree", "treeB")]
    )


def test_clean(target_tree):
    """ tree cleaning """
    lndirs.main(["-dt", target_tree, j(ROOT, "clean_tree")])
    lndirs.main(["-dct", target_tree, j(ROOT, "clean_tree")])
    assert len(os.listdir(target_tree)) == 0


def test_show(target_tree):
    """ show trees to be linked """
    lndirs.main(["-dst", target_tree,
                 j(ROOT, "linking_multitree")])
