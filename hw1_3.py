'''
Сделайте 100 get запрос к ссылке (endpoint) - https://api.kanye.rest/
Создайте словарь в питоне - пример: {'No':1, 'Joke': 'some kayne joke'},
!!! к каждой шутке прилагается номер!!)
'''

import requests
import json

url = 'https://api.kanye.rest/'

kanye_jokes = []
for i in range(1, 101):
       response = requests.get(url).json()
       jokes = {
              'No': i,
              'Joke': response['quote']
       }
       kanye_jokes.append(jokes)

print(kanye_jokes)