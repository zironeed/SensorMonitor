import os
import asyncio
import aiofiles
import aiocsv
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal


class FileProcessorThread(QThread):
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

        async with aiofiles.open(os.path.join(path_to_dir, f'output_{filename}.txt'), 'w') as file:
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

    def get_output_files(self, sensor_dir):
        with open(os.path.join(self.path_to_dirs, sensor_dir, 'output.txt')) as file:
            lines = file.readlines()
            waves = [float(line.split()[0]) for line in lines]
            values = [float(line.split()[1]) for line in lines]

        with open(os.path.join(self.path_to_dirs, sensor_dir, 'min_values.txt')) as file:
            lines = file.readlines()
            dates = [datetime.strptime((line.split()[0]), "%Y-%m-%d;%H:%M:%S") for line in lines]
            min_vals = [float(line.split()[1]) for line in lines]
        return waves, values, dates, min_vals

    def get_data(self, sensor):
        for sensor_dir in self.sensor_dirs:
            if sensor in sensor_dir:
                waves, values, dates, min_vals = self.get_output_files(sensor_dir)
                return waves, values, dates, min_vals

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
