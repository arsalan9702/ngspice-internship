from setuptools import setup, find_packages

setup(
    name='ngspice_calc',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'schemdraw',
        'jupyter',
    ],
)