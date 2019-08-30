try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from tdvt.version import __version__

setup(
    name='tdvt',
    version=__version__,
    author='Tableau',
    author_email='github@tableau.com',
    url='https://github.com/tableau/connector-plugin-sdk',
    packages=['tdvt', 'tdvt.config_gen'],
    license='MIT',
    description='A Python module for testing datasource compatability with Tableau.',
    test_suite='test',
    scripts=['tdvt_launcher.py'],
    install_requires=['defusedxml'],
    include_package_data=True
)
