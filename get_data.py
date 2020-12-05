import requests
from googletrans import Translator
from config import key_api
import requests


def take_data(city_name):
    """
    Данный фрагмет кода отвечает за:
    1) Получения информации о погоде
    :param city_name: Имя города, в котором нужно узнать погоду
    """
    city = city_name
    key_api = '08ae9239449049aed5d6d40d9b9ad307'
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + key_api
    data = requests.get(url.format(city)).json()
    return data['main']['temp']


def take_forecast_data(city):
    """
    Данный фрагмет кода отвечает за:
    1) Получения информации о прогнозе погоды
    :param city_name: Имя города, в котором нужно узнать погоду
    """
    url = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid=' + key_api
    data = requests.get(url.format(city)).json()
    data = list(filter(lambda x: x['dt_txt'].split()[1] == '12:00:00', data['list']))
    data = list(map(lambda x: x['main']['temp'], data))
    return data[:3]


def take_average_data(city):
    url = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid=' + key_api
    data = requests.get(url.format(city)).json()
    data = list(filter(lambda x: x['dt_txt'].split()[1] == '12:00:00', data['list']))
    data = list(map(lambda x: x['main']['temp'], data))
    return sum(data) / len(data)
