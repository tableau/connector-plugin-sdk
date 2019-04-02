try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from package.version import __version__

setup(
    name='package',
    version=__version__,
    author='Tableau',
    author_email='github@tableau.com',
    url='https://github.com/tableau/connector-plugin-sdk',
    packages=['package'],
    license='MIT',
    description='A Python module for packaging a Tableau connector.',
    test_suite='tests',
    python_requires='>3.7.0',
    install_requires=['xmlschema'],
    include_package_data=True
)
