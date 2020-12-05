from win10toast import ToastNotifier
from get_data import *
import datetime as dt
from time import sleep


def send_notification(city_name, date_time):
    date = date_time.split()[0]
    time = date_time.split()[1]
    notif = ToastNotifier()
    timer(date_time)
    notif.show_toast("Concord Weather",
                     "Сегодня " + date + ' ' + time + ' погода в ' + city_name + ' ' + str(
                         int(take_data(city_name))) + '°C',
                     duration=20, icon_path="img/icon.ico", )


def timer(date_notification):
    date_notification = date_notification.split()

    day = int(date_notification[0].split('.')[0])
    month = int(date_notification[0].split('.')[1])
    year = int(date_notification[0].split('.')[2])

    hours = int(date_notification[1].split(':')[0])
    minutes = int(date_notification[1].split(':')[1])

    date_notification = dt.datetime(year, month, day, hours, minutes)
    date_now = dt.datetime.now()
    time_sleep = (date_notification - date_now).days * 24 * 60 * 60 + (
                date_notification - date_now).seconds
    sleep(time_sleep)
