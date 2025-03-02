from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np
import os

# Clear any existing build directories
if os.path.exists('build'):
    import shutil
    shutil.rmtree('build')

# Specify the extension properly
extensions = [
    Extension(
        "process_files",  # Important: This should match your import name
        sources=["src/process_files.pyx"],
        include_dirs=[np.get_include()]
    )
]

setup(
    ext_modules=cythonize(extensions, annotate=True),
    package_dir={'': 'src'},  # Tell setuptools where to find source
    packages=[''],  # Needed for proper path resolution
    script_args=['build_ext', '--inplace']  # Force in-place build
)