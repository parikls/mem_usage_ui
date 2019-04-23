import pathlib
import re
from distutils.core import setup

here = pathlib.Path(__file__).parent
init = here / "mem_usage_ui" / "__init__.py"
readme_path = here / "README.md"
requirements_path = here / "requirements.txt"

with init.open() as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


with readme_path.open() as f:
    README = f.read()

with requirements_path.open() as f:
    requirements = [line for line in f.readlines()]


setup(
    name='mem_usage_ui',
    version=version,
    description='Measuring and graphing memory usage of local processes',
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
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=requirements,
    python_requires='>=3.5.3',
    entry_points={
        'console_scripts': ['mem_usage_ui = mem_usage_ui.__main__:main']
    }
)
