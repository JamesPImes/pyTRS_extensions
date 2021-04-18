
from setuptools import setup

description = 'Extension functions for the pyTRS library'

MODULE_DIR = "pytrs_ext"


def get_constant(constant):
    setters = {
        "version": "__version__ = ",
        "author": "__author__ = ",
        "author_email": "__email__ = ",
        "url": "__website__ = "
    }
    var_setter = setters[constant]
    with open(rf".\{MODULE_DIR}\_constants.py", "r") as file:
        for line in file:
            if line.startswith(var_setter):
                return line[len(var_setter):].strip('\'\n \"')
        raise RuntimeError(f"Could not get {constant} info.")


setup(
    name='pytrs_ext',
    version=get_constant("version"),
    packages=[
        'pytrs_ext',
        'pytrs_ext.trs_tools',
        'pytrs_ext.pandas_tools',
    ],
    url=get_constant("url"),
    license='Modified Academic Public License',
    author=get_constant("author"),
    author_email=get_constant("author_email"),
    description=description,
    include_package_data=True
)
