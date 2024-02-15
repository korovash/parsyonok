import re
import csv
import os
import winreg
import glob
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pathlib import Path

patterns = []
downloads_folder = ""
compiled_patterns = []

def add_match():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showinfo("Внимание", "Выберите строку для добавления совпадения.")
        return
    selected_data = tree.item(selected_item, 'values')
    summary_text.insert(tk.END, selected_data[0] + ' ')
    summary_text.see(tk.END)

def get_downloads_folder():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    value_name = "{374DE290-123F-4565-9164-39C4925E467B}"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            downloads_path, _ = winreg.QueryValueEx(key, value_name)
            return downloads_path
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_file(file_path, compiled_patterns):
    matched_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        for compiled_pattern, text, tag in compiled_patterns:
            matches = compiled_pattern.finditer(content)
            for match in matches:
                line_start = content.rfind('\n', 0, match.start()) + 1 if match.start() > 0 else 0
                line_end = content.find('\n', match.end())
                matched_line = content[line_start:line_end].strip()
                rqUID, rqTm = extract_rqUID_and_rqTm(matched_line)
                if rqUID and rqTm:
                    matched_data.append((matched_line, text, f'rqUID: {rqUID}, rqTm: {rqTm}', tag))
                else:
                    matched_data.append((matched_line, text, '', tag))
    return matched_data

def copy_solution():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showinfo("Внимание", "Выберите строку для копирования.")
        return
    selected_data = tree.item(selected_item, 'values')
    root.clipboard_clear()
    root.clipboard_append(selected_data[1])
    root.update()

def add_to_summary():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showinfo("Внимание", "Выберите строку для добавления в итоговое решение.")
        return
    selected_data = tree.item(selected_item, 'values')
    summary_text.insert('end', selected_data[1] + ' ')
    summary_text.see('end')

def add_recommendation_bbmo():
    summary_text.insert(tk.END, 'Необходимо подгрузить документы в ББМО вручную. ')

def add_recommendation_restart():
    summary_text.insert(tk.END, 'Необходимо перелогиниться в приложение (в одной вкладке браузера), очистив куки и повторить операцию. ')

def reload_log():
    global compiled_patterns 
    summary_text.delete('1.0', tk.END)

    try:
        downloads_folder = get_downloads_folder()
        list_of_files = glob.glob(os.path.join(downloads_folder, '*.txt'))

        latest_file = max(list_of_files, key=os.path.getctime)
    except:
        downloads_folder = str(Path.home() / "Downloads")
        list_of_files = glob.glob(os.path.join(downloads_folder, '*.txt'))
        latest_file = max(list_of_files, key=os.path.getctime)

    # Добавляем пометку о последнем прочитанном файле
    file_label.config(text=f"Последний прочитанный файл: {os.path.basename(latest_file)}")

    update_tree(latest_file)

    # Проверка совпадений по регулярному выражению "Счёт открыт"
    with open(latest_file, 'r', encoding='utf-8') as file:
        content = file.read()
        match = re.search(r'Счёт открыт', content)
        if match:
            summary_text.insert('end', "Счёт открыт. ")
            summary_text.see('end')

def update_tree(file_path):
    global compiled_patterns
    tree.delete(*tree.get_children())
    matched_data = parse_file(file_path, compiled_patterns)
    matched_data.sort(key=lambda x: x[0])
    for data in matched_data:
        tree.insert('', 'end', values=(data[0], data[1], data[2], data[3]))

def copy_solution():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showinfo("Внимание", "Выберите строку для копирования.")
        return
    selected_data = tree.item(selected_item, 'values')
    root.clipboard_clear()
    root.clipboard_append(summary_text.get('1.0', tk.END))
    root.update()

def copy_tag():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showinfo("Внимание", "Выберите строку для копирования тега.")
        return
    selected_data = tree.item(selected_item, 'values')
    root.clipboard_clear()
    root.clipboard_append(selected_data[3])
    root.update()

def extract_rqUID_and_rqTm(log_message):
    try:
        json_data_match = re.search(r'\{\"rqUID\"\:\"(.*?)",\"operUID\"\:\".*?",\"rqTm\"\:\"(.*?)"', log_message)
        if json_data_match.group(1) and json_data_match.group(2):
            rqUID = json_data_match.group(1)
            rqTm = json_data_match.group(2)
            return rqUID, rqTm
    except (ValueError, AttributeError):
        return '', ''
    
def add_to_summary_rqUID_Tm():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showinfo('Внимание', 'Выберите строку для добавления в итоговое решение.')
        return
    selected_data = tree.item(selected_item, 'values')
    rqUID_Tm = selected_data[2]
    summary_text.insert('end', f'{rqUID_Tm} ')
    summary_text.see('end')

def reload_patterns():
    global patterns, compiled_patterns
    patterns.clear()
    compiled_patterns.clear()

    # Чтение данных из файла patterns.csv
    try:
        with open('patterns.csv', 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                patterns.append((row[0], row[1], row[2]))
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при чтении файла patterns.csv: {e}")
        return
    
    compiled_patterns = [(re.compile(pattern), text, tag) for pattern, text, tag in patterns]
    reload_log()

def main():
    global patterns, compiled_patterns, downloads_folder

    with open('patterns.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            patterns.append((row[0], row[1], row[2]))

    compiled_patterns = [(re.compile(pattern), text, tag) for pattern, text, tag in patterns]
    # Создание основного окна
    global root
    root = tk.Tk()
    root.title("Результаты парсинга")

    # Применение темы оформления
    style = ttk.Style()
    style.theme_use('clam')

    # Определение размеров экрана
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Размеры окна
    window_width = screen_width // 2
    window_height = screen_height // 2

    # Определение координат центра экрана
    x_center = (screen_width - window_width) // 2
    y_center = (screen_height - window_height) // 2

    # Установка размеров окна и его положения
    root.geometry(f"{window_width}x{window_height}+{x_center}+{y_center}")

    # Создание таблицы
    global tree
    
    tree = ttk.Treeview(root, columns=('Совпадения', 'Решение', 'rqUID_Tm', 'Тег'))
    tree.heading('#1', text='Совпадения', anchor='w')  
    tree.heading('#2', text='Решение', anchor='w')
    tree.heading('#3', text='rqUID_Tm', anchor='w')
    tree.heading('#4', text='Тег', anchor='w')
    tree.column('#1', stretch=True, minwidth=0, width=window_width // 3)
    tree.column('#2', stretch=True, minwidth=0, width=window_width // 3)
    tree.column('#3', stretch=True, minwidth=0, width=window_width // 6)
    tree.column('#4', stretch=False, minwidth=0, width=window_width // 6)
    tree['show'] = 'headings'

    # Включение сортировки по первому столбцу
    tree.pack(fill='both', expand=True)

    # Фрейм для кнопок слева от фрейма "Итоговое решение"
    left_button_frame = tk.Frame(root)
    left_button_frame.pack(side=tk.LEFT, padx=10)

    # Ширина кнопок
    button_width = window_width // 25
    # Кнопки слева от фрейма "Итоговое решение"
    add_recommendation_bbmo_button = ttk.Button(left_button_frame, text="➕Добавить рекомендацию ББМО", command=add_recommendation_bbmo, width=button_width)
    add_recommendation_bbmo_button.pack(side=tk.TOP, pady=5)

    add_recommendation_restart_button = ttk.Button(left_button_frame, text="➕Добавить рекомендацию перезапуска", command=add_recommendation_restart, width=button_width)
    add_recommendation_restart_button.pack(side=tk.TOP, pady=5)

    add_match_button = ttk.Button(left_button_frame, text="➕Добавить совпадение", command=add_match, width=button_width)
    add_match_button.pack(side=tk.TOP, pady=5)

    add_button = ttk.Button(left_button_frame, text="➕Добавить в решение", command=add_to_summary, width=button_width)
    add_button.pack(side=tk.TOP, pady=5)

    add_to_summary_rqUID_Tm_button = ttk.Button(left_button_frame, text="➕Добавить rqUID и rqTm", command=add_to_summary_rqUID_Tm, width=button_width)
    add_to_summary_rqUID_Tm_button.pack(side=tk.TOP, pady=5)

    reload_button = ttk.Button(left_button_frame, text="🔄Перечитать лог", command=reload_log, width=button_width)
    reload_button.pack(side=tk.TOP, pady=5)

    reload_patterns_button = ttk.Button(left_button_frame, text="🔄Перегрузить шаблоны", command=reload_patterns, width=button_width)
    reload_patterns_button.pack(side=tk.TOP, pady=5)

    # Создание фрейма для итогового решения
    summary_frame = tk.Frame(root)
    summary_frame.pack(pady=10)

    # Создание текстового поля для итогового решения
    global summary_text
    summary_text = tk.Text(summary_frame, height=10, width=50, wrap=tk.WORD)
    summary_text.pack(side=tk.LEFT)

    # Пометка для последнего прочитанного файла
    global file_label
    file_label = tk.Label(root, text="", anchor="w")
    file_label.pack(pady=5)

    # Фрейм для кнопок справа от фрейма "Итоговое решение"
    right_button_frame = tk.Frame(root)
    right_button_frame.pack(side=tk.RIGHT, padx=10)

    # Кнопки справа от фрейма "Итоговое решение"
    copy_tag_button = ttk.Button(right_button_frame, text="📋Копировать ТЕГ", command=copy_tag, width=button_width)
    copy_tag_button.pack(side=tk.TOP, pady=5)

    copy_solution_button = ttk.Button(right_button_frame, text="📋Копировать решение", command=copy_solution, width=button_width)
    copy_solution_button.pack(side=tk.TOP, pady=5)

    # Обновление таблицы
    reload_log()

    # Запуск главного цикла
    root.mainloop()

if __name__ == "__main__":
    main()