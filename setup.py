from setuptools import Extension, setup
from Cython.Build import cythonize

setup(
    name='empire',
    ext_modules=cythonize('src/**/*.pyx', compiler_directives={'language_level': '3'}, annotate=True),
    package_dir={'': 'src'}
)
