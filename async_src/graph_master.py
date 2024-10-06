import os
from datetime import datetime
from pathlib import Path


class GraphMaster:
    """
    Класс для работы с графиками
    """

    def __init__(self, path_to_dirs, sensor_directories):
        self.path_to_dirs = path_to_dirs
        self.sensor_dirs = sensor_directories

    def get_min_files(self, sensor_dir):
        """
        Получение файлов минимумов
        :param sensor_dir: папка датчика
        :return: список дат, список значений минимумов
        """
        with open(os.path.join(self.path_to_dirs, sensor_dir, 'min_values.txt')) as file:
            lines = file.readlines()
            dates = [datetime.strptime((line.split()[0]), "%Y-%m-%d;%H:%M:%S") for line in lines]
            min_vals = [float(line.split()[1]) for line in lines]
        return dates, min_vals

    def get_wave_files(self, sensor_dir):
        """
        Получение файлов с волнами
        :param sensor_dir: папка датчика
        :return: спислк волн, спислк значений
        """
        sensor_path = Path(self.path_to_dirs) / sensor_dir
        for filename in os.listdir(sensor_path):
            if filename.endswith('output.txt'):
                with open(os.path.join(self.path_to_dirs, sensor_dir, filename)) as file:
                    lines = file.readlines()
                    waves = [float(line.split()[0]) for line in lines]
                    values = [float(line.split()[1]) for line in lines]

                yield waves, values

    def get_min_data(self, sensor):
        """
        Получение значений для графика минимумов
        :param sensor: имя датчика
        :return: список дат, список значений минимумов
        """
        for sensor_dir in self.sensor_dirs:
            if sensor in sensor_dir:
                dates, min_vals = self.get_min_files(sensor_dir)
                return dates, min_vals

    def get_wave_data(self, sensor):
        """
        Получение значений для графика волн
        :param sensor: имя датчика
        :return: список волн, список значений
        """
        for sensor_dir in self.sensor_dirs:
            if sensor in sensor_dir:
                yield from self.get_wave_files(sensor_dir)
                break
