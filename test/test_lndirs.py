import lndirs


def test_00():
    """ basic importing """
    lndirs.NAME
    lndirs.__version__


def test_version():
    lndirs.main(["--version"])

if __name__ == "__main__":
    test_version()
