import os
import asyncio
import aiofiles
import aiocsv
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal


class FileProcessorThread(QThread):
    """
    Класс для обработки файлов
    """
    finished = pyqtSignal()

    def __init__(self, path_to_dirs, sensor_dirs):
        super().__init__()
        self.path_to_dirs = path_to_dirs
        self.sensor_dirs = sensor_dirs
        self.output_file = 'output.txt'

    async def process_file(self, path_to_dir, filename):
        """
        Работа с одним файлом
        Вывод - данные в файле output.txt
        path_to_dir: Путь к директории датчика
        filename: Название файла
        """
        skip_rows = 14

        async with aiofiles.open(os.path.join(path_to_dir, filename), 'r') as file:
            wave, values = [], []

            reader = aiocsv.AsyncReader(file)
            async for _ in reader:
                if skip_rows == 0:
                    break
                skip_rows -= 1
                await reader.__anext__()

            async for row in reader:
                wave.append((float(row[0])))
                values.append(float(row[1].strip()))

        async with aiofiles.open(os.path.join(path_to_dir, 'min_values.txt'), 'a') as output:
            await output.write(f"{datetime.now().strftime("%Y-%m-%d;%H:%M:%S")} {min(values)}\n")

        async with aiofiles.open(os.path.join(path_to_dir, f'{filename}_output.txt'), 'w') as file:
            await file.writelines(f'{wave_v} {value_v}\n' for wave_v, value_v in zip(wave, values))

    async def get_files(self, sensor_dir):
        """
        Поиск файлов, передача их на обработку и добавление в processed_files
        sensor_dir: Путь к директории датчика
        """
        processed_files = dict()

        while True:
            for filename in os.listdir(sensor_dir):
                if filename.lower().endswith('.csv') and not processed_files.get(filename, False):
                    await self.process_file(sensor_dir, filename)
                    processed_files[filename] = True
            await asyncio.sleep(5)

    async def get_dirs(self):
        """
        Передача папок в get_files
        """
        await asyncio.gather(*[self.get_files(os.path.join(self.path_to_dirs, sensor_dir))
                               for sensor_dir in self.sensor_dirs])

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

    def run(self):
        """
        Запуск программы в потоке
        :return:
        """

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.get_dirs())
        loop.close()

    def stop(self):
        """
        Остановка работы программы
        :return:
        """

        self.finished.emit()


if __name__ == '__main__':
    processor = FileProcessorThread('C:/Users/zeroneed/Desktop/app/sample', ['DT01', 'DT02', 'DT03', 'DT04'])
    processor.run()
