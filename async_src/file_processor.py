import os
import asyncio
import aiofiles
import aiocsv
from PyQt5.QtCore import QThread, pyqtSignal


class FileProcessorThread(QThread):
    finished = pyqtSignal()

    def __init__(self, path_to_dirs):
        super().__init__()
        self.path_to_dirs = path_to_dirs
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
                wave.append((float(row[0]), float(row[1])))
                values.append(float(row[1].strip()))

        async with aiofiles.open(self.output_file, 'a') as output:
            await output.write(f"{filename}, {wave[values.index(min(values))]}, {min(values)}\n")

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
            await asyncio.sleep(4)

    async def get_dirs(self, sensor_dirs):
        """
        Передача папок в get_files
        """
        await asyncio.gather(*sensor_dirs)
