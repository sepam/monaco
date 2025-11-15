from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='monaco',
    version='0.1.2',
    author='Martijn Wieriks',
    description='Task and project estimation using Monte Carlo simulation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sepam/monaco',
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    install_requires=[
        'click>=7.0',
        'matplotlib>=3.0',
        'seaborn>=0.11',
        'numpy>=1.18',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
        ]
    },
    entry_points={
        'console_scripts': [
            'monaco=monaco.cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    keywords='monte-carlo simulation estimation project-management task-planning forecasting',
)