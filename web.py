from flask import Flask, render_template, jsonify, g, request
import re
import csv
import os
import winreg
import glob
from pathlib import Path
from utils import find_pattern
import datetime
import json

app = Flask(__name__)

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
                    matched_data.append({'Совпадения': full_line_match, 'Решения': text, 'Тег': tag})
    return matched_data

def update_tree(file_path, patterns):
    global accOpened
    global session_ids

    accOpened = False
    
    matched_data = parse_file(file_path, patterns)
    matched_data.sort(key=lambda x: x['Совпадения'])

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        if "Счёт открыт" in content:
            accOpened = True

    session_ids = []
    for item in matched_data:
        query = item['Совпадения']
        rqUid = extract_rqUid(query)
        item['rqUid'] = rqUid
        item['sessionId'] = extract_sessionId(query)
        session_id_match = re.search(r'sessionId=([^;|,]+);\s', query)
        if session_id_match:
            session_id = session_id_match.group(1)
            session_ids.append(f'"{session_id}"')
    
    return matched_data

def extract_sessionId(query):
    try:
        match = re.search(r'sessionId=([^;|,]+);\s', query)
        if match:
            sessionId = match.group(1)
            return f'{sessionId}'
        else:
            return ''
    except Exception as e:
        return f'Произошла ошибка при извлечении sessionId: {e}'

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
    
def load_log_path_from_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            return config.get('sowanalyzer', {}).get('log_path')
    except Exception as e:
        print(f"Error loading log path from config: {e}")
        return None
    
def get_log_directories(base_path):
    try:
        return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    except Exception as e:
        print(f"Error getting log directories: {e}")
        return []
    
# Маршруты для проверки некоторых триггеров (открытия счета и т.д.)
@app.route('/accOpened')
def get_acc_opened():
    return jsonify({'accOpened': accOpened})

# Базовый маршрут
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для страницы "Масс операции"
@app.route('/mass_operations')
def mass_operations():
    return render_template('mass_operations.html')

# # Маршрут для получения данных о sessionId
# @app.route('/get_session_ids')
# def get_session_ids():
#     session_ids = g.get('session_ids', [])
#     grouped_session_ids = [session_ids[i:i + 50] for i in range(0, len(session_ids), 50)]
#     return jsonify({'grouped_session_ids': grouped_session_ids})

@app.route('/data')
def get_data():
    patterns = []

    with open('patterns.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            patterns.append((row[0], row[1], row[2]))

    try:
        downloads_folder = get_downloads_folder()
        list_of_files = glob.glob(downloads_folder + '/*.txt')
        latest_file = max(list_of_files, key=os.path.getctime)
    except:
        downloads_folder = str(Path.home() / "Downloads")
        list_of_files = glob.glob(downloads_folder + '/*.txt')
        latest_file = max(list_of_files, key=os.path.getctime)

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

@app.route('/sowanalyzer', methods=['GET', 'POST'])
def sow_analyzer():
    log_path = load_log_path_from_config()
    log_directories = get_log_directories(log_path)

    if request.method == 'POST':
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        pattern = request.form.get('pattern')
        selected_directory = request.form.get('selected_directory')

        try:
            start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            end_time = datetime.datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            error_message = 'Неверный формат даты или времени'
            return render_template('sowanalyzer.html', error=error_message, log_directories=log_directories, selected_directory=log_path)

        if not start_time_str or not end_time_str:
            return render_template('sowanalyzer.html', error='Введите Дату начала и Дату конца', log_directories=log_directories, selected_directory=selected_directory)

        if not pattern:
            return render_template('sowanalyzer.html', error='Введите Pattern', log_directories=log_directories, selected_directory=selected_directory)

        results = find_pattern(pattern, os.path.join(log_path, selected_directory), start_time, end_time)
        
        return render_template('sowanalyzer.html', results=results, log_directories=log_directories, selected_directory=selected_directory)

    return render_template('sowanalyzer.html', results=None, log_directories=log_directories, selected_directory=log_path)

if __name__ == '__main__':
    app.run(debug=True)
