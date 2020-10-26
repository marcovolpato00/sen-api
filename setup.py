from setuptools import setup, find_packages

from sen_api import __version__, __author__


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='sen-api',
    version=__version__,
    author=__author__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'click',
        'halo',
        'loguru',
        'rich'
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'sen-api = sen_api.__main__:main'
        ]
    }
)
