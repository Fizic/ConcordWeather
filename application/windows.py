import sqlite3
from services import create_message, get_forecast_data, get_average_data
from notifications import *
from _thread import start_new_thread
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QAction, qApp, QMenu


class BaseTemperature(QMainWindow):
    def set_temperature(self, temperature_label, temperature_image_label, temperature: float) -> None:
        icons = ['img/temp_good.png', 'img/temp_not_good.png',
                 'img/temp_super_not_good.png']
        temperature_label.setText(str(int(temperature)) + '°C')
        if temperature >= 25:
            temperature_image_label.setPixmap(QPixmap(icons[0]))
        elif -5 <= temperature < 25:
            temperature_image_label.setPixmap(QPixmap(icons[1]))
        else:
            temperature_image_label.setPixmap(QPixmap(icons[2]))


class MainW(BaseTemperature):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/mainscreen.ui', self)
        self.con = sqlite3.connect("../cities_db.db")
        self.cur = self.con.cursor()
        self.update_information()
        self.tray()
        self.control()

    def tray(self):
        """
        Данный фрагмент кода отвечает за:
        1) Уход приложения в трей
        2) Перехват процесса завершения при нажатии на закртыие приложениея не через трей
        """
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("../img/icon.ico"))
        show_action = QAction("Открыть", self)
        quit_action = QAction("Выйти", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def control(self):
        """
        Данный фрагмент кода отвечает за:
        1) Обработку нажатий
        """
        self.clear_btn.clicked.connect(self.clear)
        self.add_btn.clicked.connect(self.add_city)
        self.update_btn.clicked.connect(self.update_information)
        self.forecast_btn_3.clicked.connect(self.open_forecast)
        self.notification_btn.clicked.connect(self.notification)
        self.average_btn.clicked.connect(self.open_average)

    def add_city(self):
        """
        Данный фрагмент кода отвечает за:
        1) Добавление города на главный экран
        """
        city_name = self.name_city.text()
        try:
            get_temperature(city_name)
        except CityDoesNotExist:
            self.label_2.setText('Город не существует')
            return
        self.name_city.clear()
        result = self.cur.execute("SELECT * FROM cities").fetchall()
        if len(result) != 3:
            self.cur.execute(f"INSERT INTO cities(name) VALUES('{city_name}')")
            self.con.commit()
            self.update_information()
            self.label_2.setText('Город добавлен')
        else:
            self.label_2.setText('Превышен лимит городов')

    def clear(self):
        """
        Данный фрагмент кода отвечает за:
        1) Очистку всех имеющихся городов с главного экрнана
        """
        widgets = [self.city_1, self.city_2, self.city_3, self.temp_1, self.temp_2,
                   self.temp_3, self.status_1, self.status_2, self.status_3]
        for widget in widgets:
            widget.setText('')
            widget.clear()
        self.cur.execute("""DELETE FROM cities""")
        self.con.commit()

    """
    Следующие 2 метода, отвечают за открытие дополнительных окон приложения
    """

    def open_forecast(self):
        city_name = self.name_city_2.text()
        try:
            get_temperature(city_name)
        except CityDoesNotExist:
            create_message('error', "Город не существует")
            return

        self.ex = ForecastScreen(city_name)
        self.ex.show()

    def open_average(self):
        city_name = self.name_city_2.text()
        try:
            get_temperature(city_name)
        except CityDoesNotExist:
            create_message('error', "Город не существует")
            return

        self.ex = AverageTemperaturesScreen(city_name)
        self.ex.show()

    def updating_city_names(self):
        """
        Данный фрагмент кода отвечает за:
        1) Обновление информации о названии городов
        """
        try:
            result = self.cur.execute("""SELECT * FROM cities""").fetchall()
        except sqlite3.OperationalError:
            self.cur.execute("CREATE TABLE cities(name varchar(255))")
            result = self.cur.execute("""SELECT * FROM cities""").fetchall()
        names_cities = [self.city_1, self.city_2, self.city_3]
        for i in range(len(result)):
            names_cities[i].setText(list(result[i])[0])

    def temperature_update(self):
        """
        Данный фрагмент кода отвечает за:
        1) Обновление информации о температуре
        """
        result = self.cur.execute("""SELECT * FROM cities""").fetchall()
        temps = [self.temp_1, self.temp_2, self.temp_3]
        statuses = [self.status_1, self.status_2, self.status_3]
        for i in range(len(result)):
            try:
                temperature = get_temperature(list(result[i])[0])
            except CityDoesNotExist:
                self.label_2.setText('Города не существует')
                return
            self.set_temperature(temps[i], statuses[i], temperature)

    def update_information(self):
        """
        Данный фрагмент кода отвечает за:
        1) Обновление данных о погоде на главном экране
        """
        self.updating_city_names()
        self.temperature_update()

    def notification(self):
        """
        Данный фрагмент кода отвечает за:
        1) Создает напоминание о погоде
        """
        city_name = self.name_city_3.text()
        date_time = self.dateTimeEdit.text()
        start_new_thread(send_notification, (city_name, date_time))

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class HomeW(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/HomeScreen.ui', self)
        self.begin_btn.clicked.connect(self.open_new_window)

    def open_new_window(self):
        self.ex = MainW()
        self.ex.show()
        self.close()


class AverageTemperaturesScreen(QMainWindow):
    def __init__(self, city_name):
        super().__init__()
        self.city_name = city_name
        uic.loadUi('design/average.ui', self)
        self.temperature_update()
        self.label.setText('Средняя температура\nв городе: -\n' + city_name)

    def temperature_update(self):
        """
        Данный фрагмент кода отвечает за:
        1) Обновление информации о температуре
        """
        icons = ['img/temp_good.png', 'img/temp_not_good.png',
                 'img/temp_super_not_good.png']
        temp = get_average_data(self.city_name)
        if temp >= 25:
            self.status_1.setPixmap(QPixmap(icons[0]))
        elif -5 <= temp < 25:
            self.status_1.setPixmap(QPixmap(icons[1]))
        else:
            self.status_1.setPixmap(QPixmap(icons[2]))
        self.temp_1.setText(str(int(temp)) + '°C')


class ForecastScreen(QMainWindow):
    def __init__(self, city_name):
        super().__init__()
        self.city_name = city_name
        uic.loadUi('design/ForecastScreen.ui', self)
        self.temperature_update()
        self.label.setText('Прогноз погоды в городе: - ' + city_name)

    def temperature_update(self):
        """
        Данный фрагмент кода отвечает за:
        1) Обновление информации о температуре
        """
        result = get_forecast_data(self.city_name)
        temps = [self.temp_1, self.temp_2, self.temp_3]
        statuses = [self.status_1, self.status_2, self.status_3]
        icons = ['img/temp_good.png', 'img/temp_not_good.png',
                 'img/temp_super_not_good.png']
        for i in range(len(result)):
            temp = result[i]
            temps[i].setText(str(int(temp)) + '°C')
            if temp >= 25:
                statuses[i].setPixmap(QPixmap(icons[0]))
            elif -5 <= temp < 25:
                statuses[i].setPixmap(QPixmap(icons[1]))
            else:
                statuses[i].setPixmap(QPixmap(icons[2]))
