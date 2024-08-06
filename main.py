import os
import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

stop_thread = False

min_wavelengths = []
min_values = []


def process_file(file, filename, output_file):
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
    global stop_thread
    processed_files = set()

    while not stop_thread:
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
    file = filedialog.asksaveasfilename(defaultextension=".txt",
                                        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file)


def start():
    global stop_thread
    stop_thread = False
    directory = directory_entry.get()
    output_file = output_entry.get()

    if not directory or not output_file:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите директорию и файл вывода.")
        return

    processing_thread = threading.Thread(target=start_processing, args=(directory, output_file))
    processing_thread.start()
    animate_graph()


def stop():
    global stop_thread
    stop_thread = True


def animate_graph():
    def update(frame):
        plt.cla()
        plt.plot(min_wavelengths, min_values, marker='o')
        plt.xlabel('Data')
        plt.ylabel('Min Value')
        plt.title('Minimum Value over Time')

    ani = FuncAnimation(plt.gcf(), update, interval=5000, cache_frame_data=False)
    plt.show()


def main():
    global directory_entry, output_entry

    root = tk.Tk()
    root.title("CSV Processor with Graph")

    tk.Label(root, text="Директория мониторинга:").grid(row=0, column=0, padx=10, pady=10)
    directory_entry = tk.Entry(root, width=50)
    directory_entry.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Выбрать", command=select_directory).grid(row=0, column=2, padx=10, pady=10)

    tk.Label(root, text="Файл вывода:").grid(row=1, column=0, padx=10, pady=10)
    output_entry = tk.Entry(root, width=50)
    output_entry.grid(row=1, column=1, padx=10, pady=10)
    tk.Button(root, text="Выбрать", command=select_output_file).grid(row=1, column=2, padx=10, pady=10)

    tk.Button(root, text="Старт", command=start).grid(row=2, column=0, padx=10, pady=10)
    tk.Button(root, text="Стоп", command=stop).grid(row=2, column=1, padx=10, pady=10)

    root.mainloop()


if __name__ == '__main__':
    main()
