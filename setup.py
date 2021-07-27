# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='elucidate_client',
    version='0.0.2',
    description='simple description',
    long_description=readme,
    author='Bram Buitendijk',
    author_email='bram.buitendijk@di.huc.knaw.nl',
    url='project_url',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
)