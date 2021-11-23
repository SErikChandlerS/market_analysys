import requests

s = requests.Session()
s.auth = ('al.badretdinov@innopolis.ru', 'VY?k1_o4')
s.headers.update({'x-test': 'true'})

# both 'x-test' and 'x-test2' are sent
s.get('https://httpbin.org/headers', headers={'x-test2': 'true'})
