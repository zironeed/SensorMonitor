import os
import time
import pandas as pd


def process_file(file, filename, output_file):
    df = pd.read_csv(file, skiprows=29, header=None, skip_blank_lines=True, sep=', ', engine='python')

    df.columns = ['Wavelength', 'Value']

    min_value = df['Value'].min()
    min_wavelength = df['Wavelength'][df['Value'].idxmin()]

    with open(output_file, 'a') as output:
        output.write(f"{filename}: {min_wavelength}, {min_value}\n")


def get_file(directory, output_file):
    processed_files = set()

    while True:
        for filename in os.listdir(directory):

            if filename.lower().endswith('.csv') and filename not in processed_files:
                file = os.path.join(directory, filename)
                process_file(file, filename, output_file)
                processed_files.add(filename)

        time.sleep(4)


def main(directory, output_file):
    get_file(directory, output_file)


if __name__ == '__main__':
    directory_path, output_path = input('Где лежат файлы?\n'), input('В какой файл записывать результаты?\n')
    main(directory_path, output_path)
