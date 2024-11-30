import asyncio
import os
import re
from aiofiles import os as aos
from PyQt5.QtCore import QThread, pyqtSignal


class GarbageCollectorThread(QThread):
    """
    Класс для удаления ненужных файлов
    """
    finished = pyqtSignal()

    def __init__(self, path_to_dirs, sensor_dirs):
        super().__init__()
        self.path_to_dirs = path_to_dirs
        self.sensor_dirs = sensor_dirs

    async def collect_old_files(self, path):
        """
        Сбор старых файлов
        :param path: Путь к папке датчика
        """

        files = await aos.listdir(path)
        files = sorted(
            (filter(lambda x: not re.search(r'(_output.txt$)|(^min_values.txt$)', x), files)),
            key=lambda x: os.path.getmtime(os.path.join(path, x))
        )
        if len(files) > 4:
            await self.delete_old_files(path, files[4::])

    @staticmethod
    async def delete_old_files(path, files):
        """
        Удаление старых файлов
        :param path: Путь к папке датчика
        :param files: Файлы для удаления
        """

        for file in files:
            await aos.remove(os.path.join(path, file))
            await aos.remove(os.path.join(path, file + '_output.txt'))

    async def garbage_process(self):
        """
        Передача папок в collect_old_files
        """

        while True:
            await asyncio.sleep(60)
            await asyncio.gather(*[self.collect_old_files(os.path.join(self.path_to_dirs, path))
                                   for path in self.sensor_dirs])

    def run(self):
        """
        Запуск программы в потоке
        :return:
        """

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.garbage_process())
        loop.close()

    def stop(self):
        """
        Остановка работы программы
        :return:
        """

        self.finished.emit()
