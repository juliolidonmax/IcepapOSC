# setup.py
from setuptools import setup
from setuptools import find_packages

# The version is updated automatically with bumpversion
# Do not update manually
__version = '0.2.1.dev0'

# windows installer:
# python setup.py bdist_wininst

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords

# ipython profile magic commands implementation
package_list = ['*ui']

# TODO: fill the long description
long_description = """ Python application to monitor and tune IcePAP 
based systems. """

# TODO: Include documentation.

classifiers = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: End Users/Desktop',
    'Topic :: Software Development :: Build Tools',
    'Topic :: Communications',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: User Interfaces',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: GNU Library or Lesser General Public ' + \
    'License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.7',
]

# TODO: Include dependencies

setup(
    name="icepaposc",
    description="Python IcePAP Extension",
    version=__version,
    author="Jarkko Inki and Roberto Homs-Puron",
    author_email="ctbeamlines@cells.es",
    url="https://github.com/ALBA-Synchrotron/IcepapOCS",
    packages=find_packages(),
    package_data={'': package_list},
    include_package_data=True,
    keywords='APP',
    license="GPL",
    long_description=long_description,
    classifiers=classifiers,
    entry_points={
        'console_scripts': [
            'icepaposc = icepaposc.__main__:main',
        ]
    }
)
