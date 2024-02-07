import json
from flask import Flask, render_template, jsonify
import re
import csv
import os
import winreg
import glob

app = Flask(__name__)


def get_documents_folder():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    value_name = "{F42EE2D3-909F-4907-8871-4C22FC0BF756}"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            downloads_path, _ = winreg.QueryValueEx(key, value_name)
            return downloads_path
    except Exception as e:
        print(f"Error: {e}")
        return None

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

def parse_file(file_path, patterns):
    matched_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for pattern, text, tag in patterns:
            for line in lines:
                matches = re.finditer(pattern, line)
                for match in matches:
                    matched_text = match.group()
                    full_line_match = line.rstrip('\n')
                    matched_data.append((full_line_match, text, tag))
    return matched_data

def update_tree(file_path, patterns):
      # Добавляем глобальные переменные для проверки некоторых триггеров
    global accOpened
    accOpened = False

    matched_data = parse_file(file_path, patterns)
    # Сортировка данных по времени (первому столбцу)
    matched_data.sort(key=lambda x: x[0])

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Проверяем наличие строки "Счёт открыт" во всем содержимом лог-файла
        if "Счёт открыт" in content:
            accOpened = True

    return [{'Совпадения': item[0], 'Решения': item[1], 'Тег': item[2], 'rqUID': extract_rqUid(item[0])} for item in matched_data]

def extract_rqUid(query):
    try:
        # Используем регулярное выражение для поиска значений rquid и rqTm в строке
        # "rqUID":"3687ebac8a004a73bb0cccb1dea26517","operUID":"3687ebac8a004a73bb0cccb1dea26517","rqTm":"2024-02-05T16:25:41"
        match = re.search(r'"rqUID":"([^"]+)","operUID":"[^"]+","rqTm":"([^"]+)"', query)
        if match:
            rqUID = match.group(1)
            rqTm = match.group(2)
            return f'rqUID: {rqUID}, rqTm: {rqTm}'
        else:
            return ''
    except Exception as e:
        return f'Произошла ошибка при извлечении rqUID и rqTm: {e}'

# Маршруты для проверки некоторых триггеров (открытия счета и т.д.)
@app.route('/accOpened')
def get_acc_opened():
    return jsonify({'accOpened': accOpened})

# Базовый маршрут
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    patterns = []
    #documents_folder = get_documents_folder()
    documents_folder = r'C:\Users\Korovan\Documents'
    with open(documents_folder + '\patterns.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            patterns.append((row[0], row[1], row[2]))

    downloads_folder = get_downloads_folder()

    if downloads_folder:
        list_of_files = glob.glob(downloads_folder + '/*.txt')
        latest_file = max(list_of_files, key=os.path.getctime)
        tree_data = update_tree(latest_file, patterns)

        # Обновленный блок для добавления rqUid в данные
        for row in tree_data:
            query = row['Совпадения']
            rqUid = extract_rqUid(query)
            row['rqUid'] = rqUid

        # Конвертируем кортежи в списки для JSON-сериализации
        tree_data = [dict(row) for row in tree_data]

        data = {
            'file_label': os.path.basename(latest_file),
            'tree_data': tree_data
        }
        
        return jsonify(data)
    else:
        return jsonify({'error': 'Не удалось получить путь к директории загрузок.'})

if __name__ == '__main__':
    app.run(debug=True)