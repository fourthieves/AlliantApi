# Alliant API

## Python Version
This is written to utilise features included in Python 3.8 so will not be compatible with earlier versions.

## Installation

To install, run `pip install git+https://github.com/fourthieves/AlliantApi.git`

## Basic Introduction

The Alliant API is a rest api developed by Real Software Systems to perform operations against the Alliant software.
This library has been written to interact with the API and abstract specific common tasks.  It heavily utilises the 
[Requests](https://pypi.org/project/requests/) library to perform the HTTP interactions, and it has a response class 
which is an extension of the Requests response and if you are familiar with Requests, then it should feel familiar.

This library will contain some methods that interact directly with the API endpoints, as well as higher level methods
that apply logic and execute across multiple endpoints to achieve specific tasks. For anyone contributing to development,
The low level access methods exist in the `Client` class, located in `client.py`.  The `AlliantAPI` class is a subclass
that utilises the low level methods in `Client` to form higher level abstractions and methods from either can 
be accessed by end users using `AlliantAPI`

## Instantiate the class

It is recommended that the context manger is used.  The Alliant API creates a session on login and the context manager 
will handle logging in as well as logging out at the end of the block, or in the event of an error.

### Instantiating the `AlliantAPI` object and authenticating

#### Determining the system layer key and application layer values
This will get the system layers from the base_url.  The `get_system_layers()` function will return a response class that
is based on the response class returned by the Requests library. The specific result of the call can be found in the 
`result` property.
```python
from alliantapi import get_system_layers

base_url = 'https://webservername/api/'

system_layers_info = get_system_layers(base_url)
print(system_layers_info.result)
```
The result will look like this `[{'key': 'default', 'displayName': 'Alliant'}]`.  It is possible to have more than one
system layer in the list, but it is uncommon.

So this example can be extended to then get the application layer as well which will be returned as a list of layer 
names. Eg: `['prod', 'test', 'dev']`
```python
from alliantapi import get_system_layers, get_application_layers

base_url = 'https://webservername/api/'

system_layers_info = get_system_layers(base_url)
system_layer_key = system_layers_info.result[0]['key']
print(system_layer_key)

application_layers_info = get_application_layers(base_url, system_layer_key)
print(application_layers_info.result)
```

Those values can then be used to instantiate the main class

```python
from alliantapi import AlliantApi

base_url = 'https://webservername/api/'

user_id = 'user'
password = 'pass'
system_layer_key = 'default'
application_layer = 'test'


with AlliantApi(base_url,
               user_id=user_id,
               password=password,
               system_layer_key=system_layer_key,
               application_layer=application_layer
               ) as aa:

    print(f"{aa.token = }  {aa.token_expires = }")
```
or utilising `**kwargs`

```python
from alliantapi import AlliantApi

kwargs = {
    'base_url': 'https://webservername/api/',
    'user_id': 'user',
    'password': 'pass',
    'system_layer_key': 'default',
    'application_layer': 'test',
}

with AlliantApi(**kwargs) as aa:
    
    print(f"{aa.token = }  {aa.token_expires = }")
```

It is possible to instantiate without the context manager, but in this case you must log in and out and an error could
lose the session token, meaning the session will consume its license until it expires.

```python
from alliantapi import AlliantApi

base_url = 'https://webservername/api/'

user_id = 'user'
password = 'pass'
system_layer_key = 'default'
application_layer = 'test'


aa = AlliantApi(base_url,
               user_id=user_id,
               password=password,
               system_layer_key=system_layer_key,
               application_layer=application_layer
               )

aa.login()

print(f"{aa.token = }  {aa.token_expires = }")

print(aa.logout())
```
# Low Level Methods

There have been a number of methods written to directly interact with the various endpoints.

## Transaction Characteristics
* lookup_user_x_collection(tc_number, number_of_records=20)
* lookup_user_x_with_filter(tc_number, filter_field,  filter_value, verbosity='default')
* lookup_user_x_guid_with_filter(tc_number, filter_field,  filter_value)
* lookup_user_x(tc_number,  guid)
* patch_user_x(tc_number, guid, body)

## Adjustment Methods
* lookup_adjustment_with_filter(filter_field,  filter_value)
* lookup_adjustment_guid_with_filter(filter_field,  filter_value)
* lookup_adjustment(guid)
* delete_adjustment(guid)
* adjustment_action(guid, action, comment=None)

## Contract Methods
* lookup_contract_with_filter(filter_field,  filter_value)
* lookup_contract_guid_with_filter(filter_field,  filter_value)
* lookup_contract(guid)
* delete_contract(guid)
* contract_action(guid, action, comment=None)