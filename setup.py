from setuptools import setup, find_packages

setup(
    name='monaco',
    version='0.1.1',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_point={
        'console_scripts': [
            'monaco=monaco.cli:main'
        ]
    }
)