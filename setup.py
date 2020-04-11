
from setuptools import setup, find_packages

setup(
    name        = 'deedee.proctoolbox',
    version     = '0.1',
    package_dir = {'': 'src'},
    packages    = find_packages(where='src'),
    author      = 'Dee Dee',
    description = 'A simple toolbox allowing to manipulate Linux processes.',
    url         = 'http://example.com/HelloWorld/'
)

