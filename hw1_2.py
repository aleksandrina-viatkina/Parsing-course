'''
2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
'''

# NASA Mars Rover Photos REST API
# Соберем фото с марсохода c информацией о них

import requests
import json
from pprint import pprint

my_key = 'ffwuA16shR1iUqFqiZpgRRQeoqDVCR6fcL1LxtfQ' # ключ сгенерирован на сайте https://api.nasa.gov/
sol_num = 100 # Сол - обозначение суток на Марсе

url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={sol_num}page=2&&api_key={my_key}'


response = requests.get(url)
j_mars_data = response.json()
pprint(j_mars_data) #вывод корректен, запишем в файл

with open ('mars_rover_photos.json', 'w', encoding= 'utf-8') as f:
       json.dump(j_mars_data, f, ensure_ascii=False, indent=4)
