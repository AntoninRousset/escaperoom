#!/usr/bin/env python

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='escaperoom',
    version='0.1a1',
    license='GPL-3',
    author='Antonin Rousset',
    description='Run and monitor an escape room',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AntoninRousset/escaperoom',
    packages=setuptools.find_packages(exclude=('logo',)),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.6, <3.8',
    install_requires=[
        'aiortc>=0.9.22'
        'aiohttp>=3.6.1'
        'aiohttp_jinja>=0.15.0'
        'aiohttp_sse>=2.0.0'
        'PJON-daemon-client>=1.0.0'
    ],
    entry_points={
        'console_scripts': [
            'escaperoom=escaperoom.__main__:main',
        ]
    }
)
