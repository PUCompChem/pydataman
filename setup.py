from setuptools import setup

NAME = "Data management"

AUTHOR = 'PUCompChem'

INSTALL_REQUIRES = [
    'matplotlib',
    'numpy',
    'pandas',
    'scikit_learn',
    'scipy',
    'requests',
    'setuptools'
]

PACKAGES = ["ioutils", "processing"]

PACKAGE_DATA = {}

CLASSIFIERS = ["Example :: Invalid"]


setup(
    name=NAME,
    author=AUTHOR,
    install_requires=INSTALL_REQUIRES,
    packages=PACKAGES,
    # package_data=PACKAGE_DATA,
    classifiers=CLASSIFIERS,
)
