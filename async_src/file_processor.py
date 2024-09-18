import os
import asyncio
import aiofiles
import aiocsv


async def process_file(path_to_files, filename, output_file):
    """
    Работа с одним файлом
    Вывод - данные в output_file
    """
    skip_rows = 14

    async with aiofiles.open(os.path.join(path_to_files, filename), 'r') as file:
        reader = aiocsv.AsyncReader(file)
        async for _ in reader:
            if skip_rows == 0:
                break
            skip_rows -= 1
            await reader.__anext__()

        async for row in reader:
            print(row)


async def get_files(my_dir, output_file):
    """
    Поиск файлов, передача их на обработку и добавление в processed_files
    """
    while True:
        for filename in os.listdir(my_dir):
            if filename.lower().endswith('.csv') and filename not in os.listdir('processed_files.txt'):
                await process_file(my_dir, filename, output_file)
        await asyncio.sleep(4)


async def get_dirs(common_dir):
    """
    Поиск папок датчиков в общей папке, передача папки в get_files
    """

    dt_dirs = [os.path.join(common_dir, d) for d in os.listdir(common_dir)
               if os.path.isdir(os.path.join(common_dir, d))]

    await asyncio.gather(*[get_files(dt_dir, f'{dt_dir}_output.txt') for dt_dir in dt_dirs])
