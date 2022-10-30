from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='r3e-api',
    description='Python binding for RaceRoom\'s Shared Memory API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1.2',    
    url='https://github.com/Yuvix25/r3e-python-api',
    author='Yuval Rosen',
    author_email='yuv.rosen@gmail.com',
    package_data={'r3e_api': ['data/*.cs']},
    packages=['r3e_api'],
    include_package_data=True,
    install_requires=[],

    classifiers=[
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
    ],
)