from setuptools import setup

setup(
    name='r3e-api',
    version='0.1.0',    
    description='Python binding for RaceRoom\'s Shared Memory API.',
    url='https://github.com/Yuvix25/r3e-python-api',
    author='Yuval Rosen',
    author_email='yuv.rosen@gmail.com',
    package_data={'r3e_api': ['*.cs']},
    packages=['r3e_api'],
    include_package_data=True,
    install_requires=[],

    classifiers=[
        'Operating System :: Windows',
        'Programming Language :: Python :: 3.7+',
    ],
)