from setuptools import setup

requires = [
    'certifi == 2021.5.30',
    'charset - normalizer == 2.0.3',
    'idna == 3.2',
    'requests == 2.26.0',
    'urllib3 == 1.26.6',
]

setup(
    name='allianrt api',
    version='0.1',
    packages=['alliantapi'],
    url='https://github.com/fourthieves/AlliantApi',
    license='',
    author='msumner',
    author_email='msumner@realsoftwaresystems.com',
    description='A library for interacting with RSS\'s Alliant software API',
    python_requires=">=3.8",
    install_requires=requires,
)
