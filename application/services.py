from PyQt5.QtWidgets import QMessageBox
from errors import CityDoesNotExist
import requests
from config import url_api


def create_message(title: str, error_message: str) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(error_message)
    msg.setWindowTitle(title)
    msg.exec()


def get_temperature(city_name):
    """
    Данный фрагмет кода отвечает за:
    1) Получения информации о погоде
    :param city_name: Имя города, в котором нужно узнать погоду
    """
    city = city_name
    data = requests.get(url_api.format(city)).json()
    try:
        temperature = int(data['main']['temp'])
    except KeyError:
        raise CityDoesNotExist
    return temperature


def get_base_data(city: str):
    data = requests.get(url_api.format(city)).json()
    data = list(filter(lambda x: x['dt_txt'].split()[1] == '12:00:00', data['list']))
    data = list(map(lambda x: x['main']['temp'], data))
    return data


def get_forecast_data(city: str) -> list:
    """
    Данный фрагмет кода отвечает за:
    1) Получения информации о прогнозе погоды
    :param city: Имя города, в котором нужно узнать погоду
    """
    data = get_base_data(city)

    return data[:3]


def get_average_data(city: str) -> float:
    data = get_base_data(city)
    if len(data) == 0:
        return 0

    return sum(data) / len(data)
