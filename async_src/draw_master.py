import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QGridLayout, QSlider
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Используем Matplotlib для встраивания графиков
from matplotlib.figure import Figure
import numpy as np  # Библиотека для работы с массивами данных и генерации случайных чисел
from PyQt5.QtCore import Qt  # Модуль для работы с базовыми типами и событиями

class SensorMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Sensor Monitor')  # Устанавливаем название окна
        self.setGeometry(100, 100, 1200, 700)  # Устанавливаем размеры окна

        self.graphs = []  # Список для хранения графиков минимумов
        self.wave_graphs = []  # Список для хранения волновых графиков
        self.sliders = []  # Список для ползунков, чтобы связать их с графиками

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

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_button)
        main_layout.addLayout(path_layout)

        # 2. Секция для датчиков
        sensors_layout = QGridLayout()  # Сетка для размещения датчиков и графиков

        # Создаем 4 блока для датчиков
        for i in range(4):
            sensor_block = self.create_sensor_block(f"DT0{i + 1}")
            sensors_layout.addLayout(sensor_block, i, 0)

        main_layout.addLayout(sensors_layout)

        # Устанавливаем главное окно
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)  # Устанавливаем основное содержимое

    def create_sensor_block(self, sensor_name):
        layout = QHBoxLayout()  # Горизонтальная разметка для датчика и его графика

        # Выбор датчика (слева)
        sensor_selection_layout = QVBoxLayout()  # Вертикальная разметка для названия датчика и выпадающего меню
        sensor_label = QLabel(sensor_name)  # Метка с названием датчика
        sensor_dropdown = QComboBox()  # Выпадающее меню для выбора датчика

        sensor_dropdown.addItems([f"DT0{i + 1}" for i in range(1, 6)])  # Пример списка датчиков
        sensor_button = QPushButton("⬇")  # Кнопка для действия с датчиком

        sensor_selection_layout.addWidget(sensor_label)
        sensor_selection_layout.addWidget(sensor_dropdown)
        sensor_selection_layout.addWidget(sensor_button)

        layout.addLayout(sensor_selection_layout)

        # 2. Волновой график
        wave_graph_label = QLabel(f"Волны для {sensor_name}")
        wave_graph = self.create_wave_graph_widget()
        layout.addWidget(wave_graph_label)
        layout.addWidget(wave_graph)

        # Новый вертикальный лэйаут для графика и ползунка
        graph_slider_layout = QVBoxLayout()

        # 3. График минимумов
        min_graph_label = QLabel(f"Минимумы для {sensor_name}")
        min_graph = self.create_graph_widget()  # Создаем график
        graph_slider_layout.addWidget(min_graph_label)
        graph_slider_layout.addWidget(min_graph)

        # 4. Ползунок для масштабирования графика
        zoom_slider = QSlider(Qt.Horizontal)  # Ползунок горизонтальный
        zoom_slider.setMinimum(1)
        zoom_slider.setMaximum(100)
        zoom_slider.setValue(10)  # Устанавливаем начальное значение масштаба
        zoom_slider.valueChanged.connect(self.update_all_graphs_zoom)  # Подключаем ползунок к изменению масштаба графиков
        graph_slider_layout.addWidget(zoom_slider)  # Правильный метод для добавления ползунка

        # Добавляем вертикальный лэйаут (график + ползунок) в горизонтальный основной лэйаут
        layout.addLayout(graph_slider_layout)

        # Добавляем график и ползунок в соответствующие списки для последующего обновления
        self.graphs.append(min_graph)
        self.sliders.append(zoom_slider)

        return layout

    def create_graph_widget(self):
        # Используем Matplotlib для создания графиков минимумов
        figure = Figure(figsize=(5, 2))  # Задаем размер графика
        canvas = FigureCanvas(figure)  # Контейнер для графика
        ax = figure.add_subplot(111)  # Добавляем ось для построения графика

        # Пример построения графика минимумов
        x = np.linspace(0, 10, 100)  # Данные по оси X
        y = np.random.uniform(-30, -10, size=len(x))  # Случайные данные минимумов по оси Y
        ax.plot(x, y)  # Построение графика

        return canvas  # Возвращаем график

    def create_wave_graph_widget(self):
        # Виджет для волнового графика

        # Используем Matplotlib для создания волновых графиков
        figure = Figure(figsize=(5, 2))  # Размер волнового графика
        canvas = FigureCanvas(figure)  # Контейнер для графика
        ax = figure.add_subplot(111)

        # Пример волновой кривой
        x = np.linspace(0, 10, 100)
        y = np.sin(x) * np.random.uniform(0.8, 1.2, size=len(x))  # Генерация колебаний
        ax.plot(x, y)

        self.wave_graphs.append(canvas)  # Сохраняем график для дальнейшего обновления

        return canvas  # Возвращаем график

    def update_all_graphs_zoom(self):
        # Обновляем масштаб для всех графиков минимумов
        for graph in self.graphs:
            zoom_value = self.sliders[self.graphs.index(graph)].value()
            ax = graph.figure.gca()  # Получаем ось графика
            ax.set_xlim([0, zoom_value])  # Изменяем масштаб по оси X
            graph.draw()  # Обновляем график


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Стандартное создание приложения PyQt
    window = SensorMonitor()  # Создаем экземпляр класса
    window.show()  # Отображаем главное окно
    sys.exit(app.exec_())  # Запускаем цикл приложения
