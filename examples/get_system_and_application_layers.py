import alliantapi

base_url = 'http://alliantwebserver/'

sl_response = alliantapi.get_system_layers(base_url=base_url)
system_layers = sl_response.result

# This assumes that a single system layer exists on the webserver. If there are more, this will return the key
# of the first one

system_layer = system_layers[0]['key']

al_response = alliantapi.get_application_layers(base_url=base_url, system_layer=system_layer)

application_layers = al_response.result

print(system_layers)
print(system_layer)
print(application_layers)