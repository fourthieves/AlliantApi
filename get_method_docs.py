import inspect
from alliantapi import AlliantApi

for name, data in inspect.getmembers(AlliantApi):
    if name.startswith('_'):
        continue

    print('Method:', name)
    print('******************************************')
    try:
        print(f'        {getattr(AlliantApi, name).__doc__.strip()}')
    except AttributeError:
        print('        No documentation included')

    print('******************************************')
