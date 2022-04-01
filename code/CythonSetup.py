"""
5-Nov-2017
Cython setup file

Compile Cyton1 & Cyton1.5 model files to C
"""


import numpy
from distutils.core import setup, Extension
from Cython.Build import cythonize


extensions = [
    Extension(
        name="src.workbench.cyton1.c1_model",
        sources=["src/workbench/cyton1/c1_model.pyx"],
        include_dirs=[numpy.get_include()]
    ),
    Extension(
        name="src.workbench.cyton15.c15_model",
        sources=["src/workbench/cyton15/c15_model.pyx"],
        include_dirs=[numpy.get_include()]
    )
]

setup(
    ext_modules=cythonize(extensions),
)
