function reloadData() {
    // Показываем индикатор загрузки
    document.getElementById('lds-roller').style.display = 'block';

    // Очищаем текущие данные
    document.getElementById('fileLabel').innerText = "";
    var tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = "";
    document.getElementById('summaryText').value = "";

    // Запрашиваем новые данные
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('fileLabel').innerText = "Последний прочитанный файл: " + data.file_label;

            var tableBody = document.getElementById('tableBody');
            tableBody.innerHTML = "";

            data.tree_data.forEach(function (row) {
                var newRow = tableBody.insertRow();
                var matchCell = newRow.insertCell(0);
                matchCell.innerHTML = highlightMessage(row.Совпадения);
                matchCell.title = row.Совпадения; // Добавляем атрибут title

                newRow.insertCell(1).innerText = row.rqUid; // rqUid
                newRow.insertCell(2).innerText = row.Решения; // Решения
                newRow.insertCell(3).innerText = row.Тег; // Тег
                newRow.insertCell(4).innerText = row.sessionId; // sessionId

                newRow.onclick = function () {
                    toggleRowSelection(this);
                };
            });

            // Скрываем индикатор загрузки после получения данных
            document.getElementById('lds-roller').style.display = 'none';

            // Запрашиваем значение accOpened
            fetch('/accOpened')
                .then(response => response.json())
                .then(accOpenedData => {
                    // Проверяем переменную accOpened и обновляем сообщение
                    if (accOpenedData.accOpened) {
                        addTextToSummary("Счёт открыт. ");
                    }
                });
        });
}

function addTextToSummary(text) {
    var summaryText = document.getElementById('summaryText');
    summaryText.focus(); // Устанавливаем фокус на textarea
    document.execCommand('insertText', false, text);
}

function toggleRowSelection(row) {
var table = document.getElementById('resultTable');
for (var i = 0; i < table.rows.length; i++) {
    // Снимаем выделение с других строк
    table.rows[i].classList.remove('selected');
}
// Выделяем текущую строку
row.classList.add('selected');
}

function addMatch() {
    // Ваш код для добавления совпадения
    var selectedRow = getSelectedRow();
    if (selectedRow) {
        var selectedText = selectedRow.cells[0].innerText;
        document.getElementById('summaryText').value += selectedText + ' ';
    }
}

function addRqUid() {
    var selectedRow = getSelectedRow();
    if (selectedRow) {
        var selectedRqUid = selectedRow.cells[1].innerText; // Предполагаем, что rqUid находится во второй ячейке
        document.getElementById('summaryText').value += selectedRqUid + ' ';
    }
}

function addToSummary() {
    // Ваш код для добавления в решение
    var selectedRow = getSelectedRow();
    if (selectedRow) {
        var selectedSolution = selectedRow.cells[2].innerText;
        addTextToSummary(selectedSolution + ' ');
    }
}

function addRecommendationBBMO() {
    // Ваш код для добавления рекомендации ББМО
    document.getElementById('summaryText').value += 'Необходимо подгрузить документы в ББМО вручную. ';
}

function addRecommendationRestart() {
    // Ваш код для добавления рекомендации перезапуска
    document.getElementById('summaryText').value += 'Необходимо перелогиниться в приложение (в одной вкладке браузера), очистив куки и повторить операцию. ';
}

function copyTag() {
    // Ваш код для копирования ТЕГА
    var selectedRow = getSelectedRow();
    if (selectedRow) {
        var selectedTag = selectedRow.cells[3].innerText;
        navigator.clipboard.writeText(selectedTag);
    }
}

function copySolution() {
    // Ваш код для копирования решения
    var summaryText = document.getElementById('summaryText');
    summaryText.select();
    document.execCommand('copy');
}

function getSelectedRow() {
    var table = document.getElementById('resultTable');
    for (var i = 0; i < table.rows.length; i++) {
        if (table.rows[i].classList.contains('selected')) {
            return table.rows[i];
        }
    }
    return null;
}

function highlightMessage(message) {
    if (message.includes('ERROR')) {
        return '<span style="color: red;">' + message + '</span>';
    } else if (message.includes('INFO')) {
        return '<span style="color: #00FF00;">' + message + '</span>';
    } else if (message.includes('WARN')) {
        return '<span style="color: yellow;">' + message + '</span>';
    } else {
        return message;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Первичное обновление данных
    reloadData();
});