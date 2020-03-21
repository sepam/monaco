from setuptools import setup, find_packages

setup(
    name='monaco',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
)