from setuptools import setup
from setuptools import find_packages

NAME = "sqlupdater"
VERSION = "0.0.1"

setup(
    name=NAME,
    version=VERSION,
    description="Up to date queries",
    author_email="introduccio@gmail.com",
    keywords=["HelloFresh", "BI", "Subscription Changes"],
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
