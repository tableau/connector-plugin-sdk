try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='tdvt',
    version='1.0',
    author='Tableau',
    author_email='github@tableau.com',
    url='https://github.com/tableau/TODO',
    packages=['tdvt', 'tdvt.config_gen'],
    license='MIT',
    description='A Python module for testing datasource compatability with Tableau.',
    test_suite='test',
    scripts=['tdvt.py', 'tdvt_runner.py'],
    include_package_data = True
)
