#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

def _get_long_description():
    sock = open('README.rst')
    long_description = sock.read()
    sock.close()
    return long_description
    


setup(
    name = 'weblayer',
    version = '0.3',
    description = '...',
    long_description = _get_long_description(),
    author = 'James Arthur',
    author_email = 'thruflo@geemail.com',
    url = 'http://github.com/thruflo/weblayer',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    license = 'http://creativecommons.org/publicdomain/zero/1.0/',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe = False,
    install_requires=[
        'zope.interface >= 3.6, < 4.0',
        'zope.component >= 3.10, < 4.0',
        # 'venusian', # ' >= 4.0, < 5.0', # @@ need to resolve this dependency link
        'webob >= 1.0, < 2.0',
        'Mako >= 0.3, < 0.4'
    ],
    extras_require = {
        'dev': [
            'setuptools_git >= 0.3, < 0.4',
            'nose >= 0.11, < 1.0',
            'coverage >= 3.4, < 4.0',
            'mock >= 0.7, < 0.8',
            'Sphinx >= 1.0, < 2.0',
            'repoze.sphinx.autointerface >= 0.4, < 0.5'
        ]
    },
    entry_points = {
        'setuptools.file_finders': [
            "foobar = setuptools_git:gitlsfiles"
        ],
        'console_scripts': [
            'weblayer-demo = weblayer.examples.helloworld:main'
        ]
    }
)
