from setuptools import setup

from lndirs import NAME

setup(
    name=NAME,
    packages=[NAME],
    setup_requires=["setuptools_scm"],
    use_scm_version=True
)
