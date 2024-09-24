import os
import sys
from copy import copy

import aiofiles
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QGridLayout, QSlider, QFileDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Используем Matplotlib для встраивания графиков
from matplotlib.figure import Figure
import numpy as np  # Библиотека для работы с массивами данных и генерации случайных чисел
from PyQt5.QtCore import Qt  # Модуль для работы с базовыми типами и событиями

from async_src.file_processor import FileProcessorThread


class SensorMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Mr. Sensor Monitor')  # Устанавливаем название окна
        self.setGeometry(100, 100, 1200, 700)  # Устанавливаем размеры окна

        self.sensor_dropdowns = []  # Список для хранения всех dropdown меню

        self.graphs = []  # Список для хранения графиков минимумов
        self.wave_graphs = []  # Список для хранения волновых графиков
        self.min_axes = []
        self.wave_axes = []
        self.wave_canvas = []
        self.min_canvas = []

        self.selected_sensors = ['None', 'None', 'None', 'None']

        self.initUI()  # Инициализация интерфейса

    def initUI(self):
        # Главное окно и разметка
        main_widget = QWidget()  # Создаем главное окно
        main_layout = QVBoxLayout()  # Вертикальная разметка для размещения элементов по порядку

        # 1. Поле для ввода пути
        path_layout = QHBoxLayout()  # Горизонтальная разметка для строки ввода и кнопки
        self.path_input = QLineEdit(self)  # Поле для ввода пути к директории

        self.path_input.setPlaceholderText("PATH/TO/DIRS")  # Плейсхолдер для поля ввода
        path_button = QPushButton("Открыть")  # Кнопка для открытия пути (здесь можно добавить логику выбора директории)
        path_button.clicked.connect(self.open_directory_dialog)    # Привязываем кнопку к функции выбора директории

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_button)
        main_layout.addLayout(path_layout)

        # 2. Секция для датчиков
        sensors_layout = QGridLayout()  # Сетка для размещения датчиков и графиков

        # Создаем 4 блока для датчиков
        for i in range(4):
            sensor_block = self.create_sensor_block(f"Monitor {i + 1}", )
            sensors_layout.addLayout(sensor_block, i, 0)

        main_layout.addLayout(sensors_layout)

        # Кнопка старта мониторинга
        self.monitor_button = QPushButton("Start Monitoring")
        self.monitor_button.clicked.connect(self.start_file_monitoring)
        main_layout.addWidget(self.monitor_button)

        # Устанавливаем главное окно
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)  # Устанавливаем основное содержимое

    def get_sensor_directories(self, directory):
        """
        Получаем все директории датчиков
        :param directory: общая директория
        :return: список названий директорий
        """
        return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

    def update_sensor_blocks(self):
        for dropdown in self.sensor_dropdowns:
            dropdown.clear()  # Очищаем предыдущее содержимое
            dropdown.addItems(self.sensor_directories)  # Добавляем реальные датчики

    def open_directory_dialog(self):
        """
        Выбор директории с папками датчиков пользователем
        :return: путь к выбранной директории
        """
        directory = QFileDialog.getExistingDirectory(self, "Выберите директорию", "")
        # Проверяем, что пользователь выбрал директорию
        if directory:
            # Сохраняем выбранный путь в поле ввода
            self.path_input.setText(directory)
            self.sensor_directories = self.get_sensor_directories(directory)
            # Сохраняем путь в переменную (можно использовать его для дальнейшей работы)
            self.update_sensor_blocks()
            return directory, self.sensor_directories

    def create_sensor_block(self, sensor_name):
        layout = QHBoxLayout()  # Горизонтальная разметка для датчика и его графика

        # Выбор датчика (слева)
        sensor_selection_layout = QVBoxLayout()  # Вертикальная разметка для названия датчика и выпадающего меню
        sensor_label = QLabel(sensor_name)  # Метка с названием датчика
        sensor_dropdown = QComboBox()  # Выпадающее меню для выбора датчика

        self.sensor_dropdowns.append(sensor_dropdown)
        sensor_button = QPushButton("⬇")  # Кнопка для действия с датчиком

        sensor_dropdown.currentIndexChanged.connect(self.on_sensor_selection_changed)

        sensor_selection_layout.addWidget(sensor_label)
        sensor_selection_layout.addWidget(sensor_dropdown)
        sensor_selection_layout.addWidget(sensor_button)

        layout.addLayout(sensor_selection_layout)

        # 2. Волновой график
        default_slider_layout = QVBoxLayout()

        wave_graph_label = QLabel(f"Волны для {sensor_name}")
        wave_graph = self.create_wave_graph_widget()
        default_slider_layout.addWidget(wave_graph_label)
        default_slider_layout.addWidget(wave_graph)

        # Новый вертикальный лэйаут для графика и ползунка
        graph_slider_layout = QVBoxLayout()

        # 3. График минимумов
        min_graph_label = QLabel(f"Минимумы для {sensor_name}")
        min_graph = self.create_graph_widget()  # Создаем график
        graph_slider_layout.addWidget(min_graph_label)
        graph_slider_layout.addWidget(min_graph)

        # Добавляем вертикальный лэйаут (график + ползунок) в горизонтальный основной лэйаут
        layout.addLayout(default_slider_layout)
        layout.addLayout(graph_slider_layout)

        # Добавляем график и ползунок в соответствующие списки для последующего обновления
        self.graphs.append(min_graph)

        return layout

    def start_file_monitoring(self):
        path_to_dirs = self.path_input.text()

        if path_to_dirs:
            # Start the file processor thread
            self.file_processor_thread = FileProcessorThread(path_to_dirs, self.sensor_directories)
            self.file_processor_thread.start()

    def create_graph_widget(self):
        # Используем Matplotlib для создания графиков минимумов
        figure = Figure(figsize=(7, 3))  # Задаем размер графика
        min_canvas = FigureCanvas(figure)  # Контейнер для графика
        ax = figure.add_subplot(111)  # Добавляем ось для построения графика

        self.min_axes.append(ax)
        self.min_canvas.append(min_canvas)

        return min_canvas  # Возвращаем график

    def create_wave_graph_widget(self):
        # Виджет для волнового графика

        # Используем Matplotlib для создания волновых графиков
        figure = Figure(figsize=(7, 3))  # Размер волнового графика
        wave_canvas = FigureCanvas(figure)  # Контейнер для графика
        ax = figure.add_subplot(111)

        self.wave_axes.append(ax)
        self.wave_canvas.append(wave_canvas)

        return wave_canvas  # Возвращаем график

    def update_graphs(self, sensor, block_index):
        """
        Обновление графиков
        """
        try:
            dates, min_vals = self.file_processor_thread.get_min_data(sensor)
        except AttributeError:
            print('Error: no file processor thread. Launch monitoring first')
            return

        min_ax = self.min_axes[block_index]
        min_ax.clear()
        min_ax.plot(dates, min_vals, color='b', marker='o', linestyle='None')
        self.min_canvas[block_index].draw()

        try:
            wave_ax = self.wave_axes[block_index]
            wave_ax.clear()
            for waves, values in self.file_processor_thread.get_wave_data(sensor):
                wave_ax.plot(waves, values, color='b', linewidth=0.5)
                self.wave_canvas[block_index].draw()
        except Exception as e:
            print(e)
            return

    def on_sensor_selection_changed(self):
        """
        Метод вызывается при изменении выбранного датчика в любом выпадающем списке.
        """
        selected_sensors = self.get_selected_sensors()
        for sensor in range(len(self.selected_sensors)):
            try:
                if self.selected_sensors[sensor] != selected_sensors[sensor]:
                    self.update_graphs(selected_sensors[sensor], sensor)
            except IndexError as e:
                print(e)
        self.selected_sensors = selected_sensors

    def get_selected_sensors(self):
        """
        Возвращает список выбранных датчиков из всех выпадающих списков.
        """
        selected_sensors = []
        for dropdown in self.sensor_dropdowns:
            selected_sensor = dropdown.currentText()  # Получаем текст выбранного элемента
            if selected_sensor:  # Проверяем, что элемент выбран
                selected_sensors.append(selected_sensor)
        return selected_sensors

