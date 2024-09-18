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

    async with aiofiles.open(output_file, 'a') as output:
        await output.write(f"{filename}, {wave[values.index(min(values))]}, {min(values)}\n")
        print(filename, wave[values.index(min(values))])


async def get_files(my_dir, output_file):
    """
    Поиск файлов, передача их на обработку и добавление в processed_files
    """
    processed_files = dict()

    while True:
        for filename in os.listdir(my_dir):
            if filename.lower().endswith('.csv') and not processed_files.get(filename, False):
                await process_file(my_dir, filename, output_file)
                processed_files[filename] = True
        await asyncio.sleep(4)


async def get_dirs(common_dir):
    """
    Поиск папок датчиков в общей папке, передача папки в get_files
    """

    dt_dirs = [os.path.join(common_dir, d) for d in os.listdir(common_dir)
               if os.path.isdir(os.path.join(common_dir, d))]

    await asyncio.gather(*[get_files(dt_dir, f'{dt_dir}/output.txt') for dt_dir in dt_dirs])
