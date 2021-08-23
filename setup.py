from setuptools import setup
from setuptools import find_packages

# The version is updated automatically with bumpversion
# Do not update manually
__version = '0.8.0'

# windows installer:
# python setup.py bdist_wininst


long_description = """ Python application to monitor and tune IcePAP based 
systems. """


setup(
    name="icepaposc",
    description="Python IcePAP Extension",
    version=__version,
    author="Jarkko Inki and Roberto Homs-Puron",
    author_email="ctbeamlines@cells.es",
    url="https://github.com/ALBA-Synchrotron/IcepapOCS",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.5',
    keywords='APP',
    license="GPL",
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
    ],
    entry_points={
        'console_scripts': [
            'icepaposc = icepaposc.__main__:main',
        ],
    },
    install_requires=[
        "pyqt5-sip",
        "icepap",
        'pyqtgraph',
        'numpy',

    ],
    package_data={'': ['*.ui', ]}
)
