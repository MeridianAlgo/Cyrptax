"""Setup script for the Crypto Tax Tool."""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='crypto-tax-tool',
    version='0.2.0',
    description='Privacy-focused cryptocurrency tax calculation tool',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Crypto Tax Tool Contributors',
    author_email='',
    url='https://github.com/MeridianAlgo/Cryptax',
    packages=find_packages(),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={
        '': ['config/*.yaml', 'config/*.conf', 'data/examples/*.csv']
    },
    install_requires=read_requirements(),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'crypto-tax-tool=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='cryptocurrency tax bitcoin ethereum accounting fifo lifo capital gains',
    project_urls={
        'Bug Reports': 'https://github.com/MeridianAlgo/Cryptax/issues',
        'Source': 'https://github.com/MeridianAlgo/Cryptax',
        'Documentation': 'https://github.com/MeridianAlgo/Cryptax/tree/main/docs',
    },
)