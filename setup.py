# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'deletion_side_effects/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-deletion-side-effects',
    version=get_version(),
    description='Provides the ability to retrieve the side effects of deleting an object in Django',
    long_description=open('README.rst').read(),
    url='https://github.com/ambitioninc/django-deletion-side-effects',
    author='Wes Kendall',
    author_email='opensource@ambition.com',
    keywords='',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django :: 1.7',
    ],
    license='MIT',
    install_requires=[
        'django>=1.7',
    ],
    tests_require=[
        'psycopg2',
        'django-nose',
        'django-dynamic-fixture',
        'mock>=1.0.1',
        'coverage>=3.7.1',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)
