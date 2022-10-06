import re
import click
import os
import datetime
import platform
from dataclasses import dataclass

PATH = ""

TITLE = ""
ABBREV = ""
GITHUB = "ryayoung" # None
PYPI = "ryayoung" # None
NAME = "Ryan Young" # None
EMAIL = "r5y@pm.me" # None
DESC = ""
VERSION = ".".join(platform.python_version().split('.')[:2])
REQUIRES = 'pandas'
KEYWORDS = ""
META = 'pyproject.toml'

# Not yet user defined
LICENSE = "MIT"
AUDIENCE = "Science/Research"
TOPIC = "Scientific/Engineering"

# Non user-defined --------------
github_url = lambda user, title: f'https://github.com/{user}/{title}'
CLASSIFIERS = lambda: {
    "License": f"OSI Approved :: {LICENSE} License",
    "Programming Language": f"Python :: {VERSION}",
    "Environment": "Console",
    "Operating System": "OS Independent",
    "Intended Audience": AUDIENCE,
    "Topic": TOPIC,
}
LINKS = lambda: {
    "Homepage": f"https://{TITLE}.com",
    "Documentation": github_url(GITHUB, TITLE),
    "Source Code": github_url(GITHUB, TITLE),
}


# FORMATTING FUNCTIONS
fmt_keywords = lambda: re.split(', |,', KEYWORDS)
fmt_requires = lambda: re.split('\W+', REQUIRES)
fmt_classifiers = lambda: [' :: '.join([k,v]) for k,v in CLASSIFIERS().items()]
fmt_links = lambda: [' = '.join([f'"{k}"', f'"{v}"']) for k,v in LINKS().items()]
# General
indented_list = lambda items: '\t' + '\n\t'.join([f'"{v}",' for v in items])
lines = lambda items: '\n'.join(items)

@click.command()
@click.argument('title')
# Value options
@click.option('--abbrev', '-a', help="Abbreviation for package name, used when importing", default=None)
@click.option('--name', '-n', help="Personal name you want displayed on pypi page", default=NAME) # prompt="Your name?"
@click.option('--github', help="Github username", default=GITHUB) # prompt="Your Github username"
@click.option('--pypi', help="PyPI username", default=PYPI) # prompt="Your PyPI username"
@click.option('--email', help="Email address", default=EMAIL) # prompt="Your email address"
@click.option('--desc', help="Short description", default=DESC) # prompt="Short description"
@click.option('--version', help="Minimum python version required", default=VERSION) # prompt="Minimum Python version required"
@click.option('--requires', help="List of required packages", default=REQUIRES) # prompt="List any required package names in a string"
@click.option('--keywords', help="List of keywords", default=KEYWORDS) # prompt="List any keywords in a comma-delimited string"
# Boolean switches
@click.option('--replace/--no-replace', help="Replace existing", default=True, show_default=True)
@click.option('--git/--no-git', help="Create an empty git repo and gitignore", default=True, show_default=True)
@click.option('--license/--no-license', help="Whether to include a LICENSE file", default=True, show_default=True)
@click.option('--readme/--no-readme', help="Whether to include a README.md file", default=True, show_default=True)
# Choice options
@click.option('--meta', help="What type of file to store metadata in",
            type=click.Choice(['pyproject', 'setup'], case_sensitive=False),
            default='pyproject', show_default=True) # prompt="How will you store metadata?"
@click.option('--template', help="File structure format",
              type=click.Choice(['single', 'src_util'], case_sensitive=False),
              default='src_util', show_default=True) # prompt="How will you structure your files?"
def fastpkg(title, abbrev, name, github, pypi, email, desc, version, requires, keywords, replace, git, license, readme, meta, template):

    global TITLE, ABBREV, NAME, GITHUB, PYPI, EMAIL, DESC, VERSION, REQUIRES, KEYWORDS, PATH
    TITLE = title
    ABBREV = abbrev if abbrev else TITLE[:2]
    NAME = name
    GITHUB = github
    PYPI = pypi
    EMAIL = email
    DESC = desc
    VERSION = version
    REQUIRES = requires
    KEYWORDS = keywords

    PATH = title + '/'

    if os.path.exists(TITLE):
        if replace:
            os.system(f'rm -r {TITLE}')
        else:
            raise click.ClickException(f'Directory with name, {TITLE}, already exists. Try again')

    os.mkdir(TITLE)

    if git:
        add_git()

    if license:
        add_license()

    if readme:
        add_readme()

    meta_options[meta]()

    code_template = CodeTemplate()
    getattr(code_template, template).write()


def write_file(path, text):
    with open(path, 'w') as f:
        f.write(text)


def add_git():
    os.system(f'cd {TITLE}; git init; git remote add origin git@github.com:{GITHUB}/{TITLE}.git')
    write_file(PATH + '.gitignore',
'''dist
test
*__pycache__
*.ipynb_checkpoints
*.egg-info

.DS_Store
*test.py

*.ipynb
*.docx
*.csv
*.xlsx
*.ai
*.pkl
''')


def add_license():
    write_file(PATH + 'LICENSE',
f'''Copyright (C) {datetime.date.today().year} {NAME}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')


def add_readme():
    pypi = f'https://pypi.org/project/{TITLE}/'
    shield = f'https://img.shields.io/pypi/v/{TITLE}.svg'

    write_file(PATH + 'README.md',
f'''<h1> {TITLE} &nbsp;&nbsp;&nbsp; <a href="{pypi}" alt="Version"> <img src="{shield}" /></a> </h1>

#### [Source code]({github_url(GITHUB, TITLE)})

<br>

> {DESC}

<br>

## Install & Use

```text
pip install {TITLE}
```

```py
import {TITLE} as {ABBREV}
```

> **Must have Python {VERSION} or higher**

---
''')


def add_meta_pyproject():
    write_file(PATH + 'pyproject.toml',
f'''[build-system]
# requires: list of packages needed to build my package
requires = ["hatchling"]
# build-backend: name of the python object that frontends use to perform build
build-backend = "hatchling.build"

[project]
name = "{TITLE}"
version = "0.0.0"
requires-python = ">={VERSION}"

description = "{DESC}"

readme = "README.md"
license = {{ file = "LICENSE" }}

authors = [
    {{ name = "{NAME}", email = "{EMAIL}" }},
]

maintainers = [
    {{ name = "{NAME}", email = "{EMAIL}" }},
]

dependencies = [
{indented_list(fmt_requires())}
]

classifiers = [
{indented_list(fmt_classifiers())}
]

keywords = [
{indented_list(fmt_keywords())}
]


[project.urls]
{lines(fmt_links())}
''')


def add_meta_setup():
    write_file(PATH + 'setup.cfg',
f'''[metadata]
description_file=README.md
license_files=LICENSE
''')

    write_file(PATH + 'setup.py',
f'''import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
name="{TITLE}",
version="0.0.0",
description="{DESC}",
long_description=README,
long_description_content_type="text/markdown",
url="{github_url(GITHUB, TITLE)}",
license="{LICENSE}",

author="{NAME}",
author_email="{EMAIL}",
packages=find_packages("src"),
package_dir={{"": "src"}},

classifiers = [
{indented_list(fmt_classifiers())}
],

keywords = [
{indented_list(fmt_keywords())}
],

install_requires = [
{indented_list(fmt_requires())}
],

python_requires = ">={VERSION}"
)
''')



meta_options = {
    'pyproject': add_meta_pyproject,
    'setup': add_meta_setup,
}


class CodeStruct(dict):

    def _imports(self, root_path, modules):
        return '\n'.join([f'from {root_path}{m} import *' for m in modules])

    def write(self):
        '''
        Recursive process:
        Iterate through key-vals in dict. If value is a string,
        create a new file using key as the name and writing its value to it.
        If key is a python file and there are sub-dirs in the current dir, write
        to it an import * statement for each of the sub-dirs.
        If the value is a dict, add the key to the end of the current path,
        create a new directory for the updated path, and recursively call this
        function for each of the key-val pairs inside the dict. But before any
        recursion, we have a couple things to do:
        - If there are any subdirectories in the current dir, loop through each
          python file (except init) in the current dir and set its value to import
          * from each of thoes subdirectories.
        - Check if we're inside the root of the project yet (we enter
          the root once the key matches the project title). If we are, advance the
          root path with the current key, create a key-val pair inside the dict
          for an __init__.py file, setting its value (text to be written) to import
          star from every python file and sub-dir inside the current dir. Since the
          recursion will continue, those sub-dirs will end up having their own init
          files which import all of their contents, and so on. This way, the developer
          will have easy access to all code during early development.
        '''
        for k,v in self.items():
            self._write_rec(PATH, "", False, k, v)

    def _write_rec(self, path, root_path, in_root, key, val):

        def get_subdirs(items):
            return [i for i in items if '.' not in i]

        def get_py_files(items):
            return [i.split('.')[0] for i in items if i.endswith('.py') and i != '__init__.py']

        if val == None:
            val = ''
        if isinstance(val, str):
            write_file(path + key, val)
        else:
            subdirs = get_subdirs(val.keys())
            py_files = get_py_files(val.keys())

            if len(subdirs) > 0:
                text = self._imports(root_path, subdirs)
                for name in py_files:
                    if val[name + '.py'] is None:
                        val[name + '.py'] = text

            if key == TITLE:
                in_root = True
            if in_root:
                root_path += key + "."
                # Select only directories and .py files, excluding init
                modules = subdirs + py_files
                val['__init__.py'] = self._imports(root_path, modules)

            path += key + "/"
            os.mkdir(path)
            for k,v in val.items():
                self._write_rec(path, root_path, in_root, k, v)



import inspect
import types
def funcs_as_properties(cls):
    for name, m in inspect.getmembers(cls, lambda x: inspect.isfunction(x)):
        if not name.startswith('_'):
            setattr(cls, name, property(m))
    return cls


@funcs_as_properties
class CodeTemplate:

    @staticmethod
    def _imports(modules):
        return '\n'.join([f'from {TITLE}.{m} import *' for m in modules])

    def single(self):
        return CodeStruct({ f'{TITLE}.py': ''})

    def src_util(self):
        return CodeStruct({
            'src': {
                'test.py': f'import {TITLE} as {ABBREV}',
                'test.ipynb': None,
                TITLE: {
                    'main.py': None,
                    'util': {
                        'util.py': None,
                    }
                }
            }
        })



# cls = CodeTemplate
# funcs = {i: getattr(cls, i) for i in dir(cls) if not i.startswith('__') and callable(getattr(cls, i))}
# for name, func in funcs.items():
    # setattr(cls, name, property(func))





# EXAMPLE setup.cfg
'''
[metadata]
description_file=README.md
license_files=LICENSE
'''

# EXAMPLE setup.py
'''
import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name='tsopt',
    version='0.0.35',
    description="Easily solve any multi-stage transshipment cost minimization optimization problem",
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/ryayoung/tsopt',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    author="Ryan Young",
    author_email='ryanyoung99@live.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    keywords=['supply chain', 'optimization', 'inventory'],
    install_requires=[
          'pandas',
          'matplotlib',
          'seaborn',
          'pulp',
    ],
    python_requires='>=3.9'
)
'''

# ICONS FOR PROJECT URLS
# https://github.com/pypi/warehouse/blob/01f87cfdb6275a8c8bc11b838618df246fc10fec/warehouse/templates/packaging/detail.html
