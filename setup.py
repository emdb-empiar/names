from setuptools import setup, find_packages

setup(
    name='names',
    version='0.1.0',
    packages=find_packages(),
    url='',
    license='Apache 2.0',
    author='Paul K. Korir, Andrii Iudin, Sriram Somasundharam',
    author_email='pkorir@ebi.ac.uk, paul.korir@gmail.com',
    description='EMDB, EMPIAR and ARIA entry names',
    install_requires=['noid'],
)
