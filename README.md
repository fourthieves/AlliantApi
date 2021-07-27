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

## Create an AlliantApi object

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

# Available Methods

## Low Level Methods

There have been a number of methods written to directly interact with the various endpoints.

### Adjustment Methods
* lookup_adjustment_with_filter(filter_field,  filter_value)
* lookup_adjustment_guid_with_filter(filter_field,  filter_value)
* lookup_adjustment(guid)
* delete_adjustment(guid)
* adjustment_action(guid, action, comment=None)

### Contract Methods
* lookup_contract_with_filter(filter_field,  filter_value)
* lookup_contract_guid_with_filter(filter_field,  filter_value)
* lookup_contract(guid)
* delete_contract(guid)
* contract_action(guid, action, comment=None)

### Transaction Characteristics
* lookup_user_x_collection(tc_number, number_of_records=20)
* lookup_user_x_with_filter(tc_number, filter_field,  filter_value, verbosity='default')
* lookup_user_x_guid_with_filter(tc_number, filter_field,  filter_value)
* lookup_user_x(tc_number,  guid)
* patch_user_x(tc_number, guid, body)

# The AlliantApiResponse object

When you make an API call with a low level method, an AlliantApiResponse object is returned. There is a bit of an 
overlap between the AlliantApiResponse object, and the Response object that is returned by the Requests libray for anyone
familiar with that library.

There is a base response object, and this is extended for certain types of call.

The base AlliantApiResponse object has the following properties related to the response

| Property           | Datatype               | Explanation                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|--------------------|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| elapsed            | datetime               | The amount of time elapsed between sending the request and the arrival of the response (as a timedelta). This property specifically measures the time   taken between sending the first byte of the request and finishing parsing the   headers.                                                                                                                                                                                                  |
| encoding           | str                    | Encoding to decode with when accessing r.text.                                                                                                                                                                                                                                                                                                                                                                                                    |
| errors             | list of dicts          | A list of all of the error returned                                                                                                                                                                                                                                                                                                                                                                                                               |
| has_errors         | bool                   | Returns `True` if there are any errors in the errors property                                                                                                                                                                                                                                                                                                                                                                                     |
| has_warnings       | bool                   | Returns `True` if there are any warnings in the warnings property                                                                                                                                                                                                                                                                                                                                                                                 |
| headers            | dict                   | Case-insensitive Dictionary of Response Headers. For example, `headers['content-encoding']` will return the value of a 'Content-Encoding' response header.                                                                                                                                                                                                                                                                                        |
| ok                 | bool                   | Returns `True` if status_code is less than 400, `False` if not. This attribute checks if the status code of the response is between 400 and 600 to see if there was a client error or a server error. If the status code   is between 200 and 400, this will return True. This is not a check to see if the response code is 200 OK.                                                                                                              |
| raise_for_status() | exception              | Raises `HTTPError`, if one occurred.                                                                                                                                                                                                                                                                                                                                                                                                              |
| reason             | str                    | Textual reason   of responded HTTP Status, e.g. “Not Found” or “OK”                                                                                                                                                                                                                                                                                                                                                                               |
| request            | RequestFormat          | Returns a RequestFormat object with the following properties:<br/> *`method` _str_ <br/> *`url` _str_<br/> *`body` _str_<br/> *`headers` _str_                                                                                                                                                                                                                                                                                                    |
| result             | list of dicts, or dict | the content of the result key in the JSON returned by the API.                                                                                                                                                                                                                                                                                                                                                                                    |
| status_code        | int                    | Integer Code   of responded HTTP Status, e.g. 404 or 200.                                                                                                                                                                                                                                                                                                                                                                                         |
| text               | str                    | Content of the response, in unicode. <br/><br/>If Response.encoding is None, encoding will be guessed using charset_normalizer or chardet. <br/><br/>  The encoding of the response content is determined based solely on HTTP headers, following RFC 2616 to the letter. If you can take advantage of non-HTTP knowledge to make a better guess at the encoding, you should set r.encoding appropriately before accessing this property.         |
| url                | str                    | Final URL   location of Response.                                                                                                                                                                                                                                                                                                                                                                                                                 |
| warnings           | list of dicts          | A list of all the warnings returned                                                                                                                                                                                                                                                                                                                                                                                                               |

## Adjustments 
Adjustments are extended with an `adjustment_status` property

## Collections 
Collections are extended with an `items` property that returns the _list_ of objects in the collection, from the result 

## Contracts
Contracts are extended with a `contract_status` property

