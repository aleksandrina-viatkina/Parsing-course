'''
1. Посмотреть документацию к API GitHub,
разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
'''

import requests
import json

# https://api.github.com/users/USERNAME/repos <- из документации, как должна выглядеть ссылка
#https://api.github.com/users/aleksandrina-viatkina/repos

main_link = 'https://api.github.com'
user_name = 'aleksandrina-viatkina'

response = requests.get(f'{main_link}/users/{user_name}/repos')

j_data = response.json()
for i in j_data:
   print(i['name']) # вывод корректный, далее сохраним в файл

with open (f'{user_name}.json', 'w', encoding= 'utf-8') as f:
    json.dump(j_data, f, ensure_ascii=False, indent=4)




