import os
import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

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


def start_processing(directory, output_file):
    try:
        get_file(directory, output_file)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def select_directory():
    directory = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(0, directory)


def select_output_file():
    file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file)


def start():
    directory = directory_entry.get()
    output_file = output_entry.get()

    if not directory or not output_file:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите директорию и файл вывода.")
        return

    start_processing(directory, output_file)


# Создание основного окна
root = tk.Tk()
root.title("CSV Processor")

# Метки и поля ввода
tk.Label(root, text="Выберите директорию:").grid(row=0, column=0, padx=10, pady=5)
directory_entry = tk.Entry(root, width=50)
directory_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Выбрать", command=select_directory).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Выберите файл вывода:").grid(row=1, column=0, padx=10, pady=5)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Выбрать", command=select_output_file).grid(row=1, column=2, padx=10, pady=5)

# Кнопка для начала обработки
tk.Button(root, text="Начать", command=start).grid(row=2, column=0, columnspan=3, pady=10)

# Запуск главного цикла приложения
root.mainloop()
