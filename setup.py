from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import setup
from setuptools import find_packages


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="liquidpy",
    version="1.0.0",
    license="MIT License",
    description="Cryptocurrency trading library for LIQUID BY QUOINE.",
    author="mitsutoshi",
    url=f"https://github.com/mitsutoshi/liquidpy",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob('liquidpy/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=_requires_from_file('requirements.txt'),
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov"]
)