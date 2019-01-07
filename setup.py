import os
from distutils.core import setup


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open("requirements.txt") as f:
    requirements = [line for line in f.readlines()]

setup(
    name='mem_usage_ui',
    version='0.5',
    description='UI for memory usage of processes',
    long_description=README,
    author='Dmytro Smyk',
    author_email='porovozls@gmail.com',
    url='https://github.com/parikls/mem_usage_ui',
    packages=["mem_usage_ui"],
    package_data={
        'mem_usage_ui': ['templates/index.html', 'static/js/build.js']
    },
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=requirements,
    entry_points={
        'console_scripts': ['mem_usage_ui = mem_usage_ui.__main__:main']
    }
)
