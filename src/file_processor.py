import os
import time
import pandas as pd


min_wavelengths, min_values = [], []


def process_file(file, filename, output_file):
    """
    Обработка значений CSV-файла
    :param file: полный путь к CSV-файлу
    :param filename: имя CSV-файла
    :param output_file: файл вывода значений
    """
    try:
        df = pd.read_csv(file, skiprows=29, header=None, skip_blank_lines=True, sep=', ', engine='python')
        df.columns = ['Data', 'Value']
        min_value = df['Value'].min()
        min_wavelength = df['Data'][df['Value'].idxmin()]

        min_wavelengths.append(min_wavelength)
        min_values.append(min_value)

        with open(output_file, 'a') as output:
            output.write(f"{filename}: {min_wavelength}, {min_value}\n")
    except Exception as e:
        print(f"Error processing {file}: {e}")


def get_file(directory, output_file):
    """
    Поиск файлов, обработка значений файлов и сохранение файла как обработанного
    :param directory: папка мониторинга
    :param output_file: файл вывода значений
    """
    processed_files = set()

    while True:
        for filename in os.listdir(directory):
            if filename.lower().endswith('.csv') and filename not in processed_files:
                file = os.path.join(directory, filename)
                process_file(file, filename, output_file)
                processed_files.add(filename)
        time.sleep(4)
