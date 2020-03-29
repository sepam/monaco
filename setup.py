from setuptools import setup, find_packages

setup(
    name='monaco',
    version='0.1.2',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_points={
        'console_scripts': [
            'monaco=monaco.cli:main'
        ]
    }
)