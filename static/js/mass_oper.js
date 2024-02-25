var sessionIdsResult = [];
var rqUIDResult = [];

function handleFile() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];

    if (file) {
        var reader = new FileReader();
        reader.onload = function (e) {
            var content = e.target.result;
            extractAndGenDLSessionIds(content);
        };
        reader.readAsText(file);
    }
}

function handleFilterqUID() {
    var fileInput = document.getElementById('fileInputrqUID');
    var file = fileInput.files[0];

    if (file) {
        var reader = new FileReader();
        reader.onload = function (e) {
            var content = e.target.result;
            extractAndGenDLrqUID(content);
        };
        reader.readAsText(file);
    }
}

function extractSessionIds(content) {
    var sessionIdRegex = /\bsessionId=([^;]+)/g;
    var matches = [];
    var match;
    while ((match = sessionIdRegex.exec(content)) !== null) {
        matches.push([match[1]]);
    }

    return matches;
    // return matches ? matches.map(match => match.split('=')[1].trim()) : [];
}

function extractrqUID(content) {
    var rqUIDRegex = /"rqUID":"([^"]+)","operUID":"[^"]+","rqTm":"([^"]+)"/g;
    var matches = [];
    var match;

    while ((match = rqUIDRegex.exec(content)) !== null) {
        matches.push([match[1], match[2]]);
    }

    return matches;
}

function extractAndGenDLSessionIds(content) {
    var sessionIds = Array.from(new Set(extractSessionIds(content)));
    // uniquesessionIds = new Set(sessionIds);
    // var sessionIdsArray = Array.from(uniquesessionIds);
    sessionIdsResult = sessionIdsResult.concat(sessionIds);
    createDownloadIcon(sessionIdsResult, 'sessionIds.csv', formatSessionIds);
}

function extractAndGenDLrqUID(content) {
    var rqUIDIds = extractrqUID(content);
    rqUIDResult = rqUIDResult.concat(rqUIDIds);
    createDownloadIcon(rqUIDResult, 'rqUID.csv', formatrqUID);
}

function createDownloadIcon(data, filename, format) {
    var formattedData = data.map(item => format(item)).join('\n');

    var blob = new Blob([formattedData], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);

    var downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = filename;
    // downloadLink.innerText = 'Скачать результаты';
    downloadLink.innerHTML = '&#128190; Скачать результаты'; // Добавляем символ дискеты
    downloadLink.style.color = 'white'; // Устанавливаем цвет текста

    var iconContainer = document.getElementById('downloadIconContainer');
    iconContainer.innerHTML = '';  // Очищаем содержимое контейнера
    iconContainer.appendChild(downloadLink);
}

function formatSessionIds(item) {
    return item.join(',');
}

function formatrqUID(item) {
    return `${item[0]},${item[1]}`;
}