import os
import re

from itertools import chain

from setuptools import (
    find_packages,
    setup,
)

REQUIREMENTS_DIR = os.path.join(os.path.dirname(__file__), 'requirements')


def get_version(package_path):
    """Extract and version number from given package's '__init__.py'.
    """
    init_path = os.path.join(package_path, '__init__.py')
    match = re.search(r"__version__ = '([^']+)'", open(init_path).read(), re.M)
    return match.group(1)


def get_install_requires_list(
    requirements_file,
    requirements_dir=REQUIREMENTS_DIR,
):
    """Create a list of packages from the given requirements file.
    """
    requirements = list()
    with open(requirements_file) as f:
        for line in f.readlines():
            if line.startswith('-r'):
                rpath = line.split(' ')[-1].strip()
                if not rpath.startswith(requirements_dir):
                    rpath = os.path.join(requirements_dir, rpath)
                requirements = chain(
                    requirements,
                    get_install_requires_list(rpath),
                )
            else:
                requirements.append(line)
    return list(set(requirements))


setup(
    name='jobsbrowser_backend',
    version=get_version('api'),
    packages=find_packages(include=('api*',)),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=get_install_requires_list('requirements.txt'),
    zip_safe=False,
)
