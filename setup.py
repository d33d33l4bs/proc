
from setuptools import setup, find_packages

setup(
    name        = 'deedee.proc',
    version     = '0.1',
    package_dir = {'': 'src'},
    packages    = find_packages(where='src'),
    author      = 'Dee Dee',
    description = 'A simple toolbox allowing to manipulate Linux processes.',
    url         = 'https://github.com/d33d33l4bs/proc'
)

