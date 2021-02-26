try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from connector_packager.version import __version__

setup(
    name='connector_packager',
    version=__version__,
    author='Tableau',
    author_email='github@tableau.com',
    url='https://github.com/tableau/connector-plugin-sdk',
    packages=['connector_packager'],
    license='MIT',
    description='A Python module for packaging a Tableau connector.',
    test_suite='tests',
    python_requires='>3.7',
    install_requires=['xmlschema', 'defusedxml', 'packaging'],
    tests_require=['six'],
    include_package_data=True
)
