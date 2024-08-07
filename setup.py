from setuptools import find_packages, setup


NAME = "pydataman"

AUTHOR = "PUCompChem"

VERSION = "0.0.1"

INSTALL_REQUIRES = [
    'matplotlib',
    'numpy',
    'pandas',
    'scikit_learn',
    'scipy',
    'requests',
    'setuptools'
]


PACKAGES = find_packages(where='src')

PACKAGE_DIR = {'': 'src'}

#PACKAGE_DATA = {}

CLASSIFIERS = ["Example :: Invalid"]


setup(
    name=NAME,
    author=AUTHOR,
    install_requires=INSTALL_REQUIRES,
    packages=PACKAGES,
    package_dir=PACKAGE_DIR,
    # package_data=PACKAGE_DATA,
    classifiers=CLASSIFIERS,
    version=VERSION
)
