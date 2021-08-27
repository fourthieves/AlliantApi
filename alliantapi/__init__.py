"""
The Alliant API is a rest api developed by Real Software Systems to perform operations against the Alliant software.
This library has been written to interact with the API and abstract specific common tasks. It heavily utilises the
Requests library to perform the HTTP interactions, and it has a response class which is an extension of the Requests
response and if you are familiar with Requests, then it should feel familiar.

This library will contain some methods that interact directly with the API endpoints, as well as higher level methods
that apply logic and execute across multiple endpoints to achieve specific tasks. For anyone contributing to
development, The low level access methods exist in the Client class, located in client.py. The AlliantAPI class is a
subclass that utilises the low level methods in Client to form higher level abstractions and methods from either can be
accessed by end users using AlliantAPI
"""

from .client import get_system_layers, get_application_layers
from .resource import AlliantApi

