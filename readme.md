# Description:
Простая программа на Python, которая берет последний записанный файл txt из директории Downloads и проводит проверку по регулярным выражениям из файла patterns.csv, выдавая на форму совпадения, если они имееются.

# Prereq:
0. Пока что операционная система для запуска только Windows, хост, с которого подразумевается выполнение - ВАРМ Альфа.
1. Установленный интерпретатор Python версии из SberUserSoft.
2. [ИЗМЕНЕНО]Файл patterns.csv может лежать в директории запуска, но нужно переходить в эту директорию до запуска (выполнить cd путь_до_файлов).
3. Файлы логов будут проверяться только по расширению txt и если находяться в директории Downloads

# HowTo:
Директория Downloads, Documents вычисляется автоматически, исходя из значений реестра Windows (сделано для обходя проблем с путями windows в среде ВАРМ, т.к. там эти директории перенаправлены на сетевой ресурс)
Выполнить скрипт можно примерно следующей командой в cmd или powershell:

    cd \\werde267.ca.sbrf.ru\VOL1_FolderRedirection\STD-VARM\21479579_OMEGA\Documents\parsyonok
    python app.py

Запуск сразу же проверит последний файл лога из Downloads и выдаст результаты на форму, если будут совпадения. Если в файле лога есть сообщение "счёт открыт", то это сразу добавится в итоговое решение. Текстбокс итогово решения можно редактировать и руками, кнопки существуют для ускорения процесса обработки.

Кнопки:
<pre><b>Перечитать лог</b> - очищает данные формы и перечитывает последний файл лога.
<b>Добавить решение</b> - добавляет <b>решение</b> из выбранной строки столбца "Решение" в окно итогового решения
<b>Добавить совпадение</b> - добавляет <b>совпадение</b> из выбранной строки столбца "Совпадение" в окно итогового решения
<b>Добавить рекомендацию перезапуска</b> - добавляет текст 'Необходимо перелогиниться в приложение (в одной вкладке браузера), очистив куки и повторить операцию. ' в окно итогового решения
<b>Добавить рекомендацию ББМО</b> - добавляет текст 'Необходимо подгрузить документы в ББМО вручную. ' в окно итогового решения
<b>Копировать ТЕГ</b> - Копирует ТЕГ из выбранной строки столбца ТЕГ в буфер обмена для дальнейшей вставки в заявку HPSM
<b>Копировать решение</b> - Копирует содержимое окна итогово решения в буфер обмена для дальнейшей вставки в заявку HPSM
</pre>

# Example case:
Например, у нас спраслися файл и на экране мы видим следующее\
![plot](./example/parsyonok_ex1.png)\
Тут мы сразу получаем сообщение в итоговое решение, что счет открыт. Оставим его и выберем строку 3, т.к. скорее всего, это последнее исключение, которое и увидел пользователь. Нажмем <b>Добавить решение</b>, т.к. хотим обогатить итоговое решение информацией, что случилось и/или что следует сделать.

![plot](./example/parsyonok_ex2.png)\
Дальше смотрим, что, скорее всего, у пользователя по заявке возникли проблемы с документами и нажмем <b>Добавить рекомендацию ББМО</b>, чтобы обогатить итоговое решение информацией о том, что требуется догрузить документы в ББМО.

![plot](./example/parsyonok_ex3.png)\
На этом наше итоговое решение достаточно полное, и можно копировать ТЕГ, который принадлежит данному исключению и вставлять его в заявку. Далее копировать само решение и добавлять в заявку

# Source file
Файл patterns.csv содержит строки по 3 значения, разделеные запятыми, по которым происходят проверки по регулярным выражениям и добавление решений и тегов.
Возьмем строку, по которой выполнилось совпадение из примера выше:\
    <b>VSPLE_ACCOUNT_OPENING_BH.+Exception with message \[for state \[kopiop\]</b>,"Вероятная причина ошибки: использование браузерной кнопки <Назад на форме [kopiop]","error_back_btn_kopiop"\
Выделенная часть - регулярное выражение, по которому выполняется поиск в файлах (Совпадение)\
    VSPLE_ACCOUNT_OPENING_BH.+Exception with message \[for state \[kopiop\],<b>"Вероятная причина ошибки: использование браузерной кнопки <Назад на форме [kopiop]"</b>,"error_back_btn_kopiop"\
Эта выделенная часть - строка "Решение", которое показывается в столбце "Решение"\
    VSPLE_ACCOUNT_OPENING_BH.+Exception with message \[for state \[kopiop\],"Вероятная причина ошибки: использование браузерной кнопки <Назад на форме [kopiop]",<b>"error_back_btn_kopiop"</b>\
Эта выделенная часть - строка "ТЕГ", которое показывается в столбце "ТЕГ"\

# Web-версия

Prereq:
    Т.к. веб-версия использует библиотеку Flask для Python, нужно ее сначала установить
    Сделать это можно следующим образом в omega.sbrf.ru:
    
    Настройка локального пк для работы с OCS
    - идем сначала сюда - https://sberosc.ca.sbrf.ru/dashboard/profile/
    - там генерируем токен и сохраняем
    - идем сюда через проводник: %appdata% (должен открыться путь C:\Users\USERNAME\AppData\Roaming) 
    - Создаем папку pip
    - Внутри папки pip делаем файл pip.ini
    - В файле пишем следующую конфигурацию:
        [global]
        index_url=https://token:ВАШ_ТОКЕН@sberosc.ca.sbrf.ru/repo/pypi/simple
        trusted-host=sberosc.ca.sbrf.ru
        default_timeout=90
    - Сохраняем и выполняем в CMD/Powershell:
        pip install flask

Запуск веб-сервера выглядит примерно так:
    cd \\werde267.ca.sbrf.ru\VOL1_FolderRedirection\STD-VARM\21479579_OMEGA\Documents\parsyonok
    python web.py

Доступен в браузере по ссылке: http://127.0.0.1:5000

Вкладка "Масс операции", пока в разработке =)