from setuptools import setup

requires = [
    'requests>=2.26.0',
]

setup(
    name='alliantapi',
    version='0.0.1',
    packages=['alliantapi'],
    url='https://github.com/fourthieves/AlliantApi',
    license='',
    author='msumner',
    author_email='msumner@realsoftwaresystems.com',
    description='A library for interacting with RSS\'s Alliant software API',
    python_requires=">=3.8",
    install_requires=requires,
)
