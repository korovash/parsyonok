function selectDirectory() {
    // Обработка изменений в выпадающем списке
    const logDirectorySelect = document.getElementById('log_directory');
    const selectedDirectory = logDirectorySelect.options[logDirectorySelect.selectedIndex].value;
    const pathInput = document.getElementById('path');
    pathInput.value = selectedDirectory;
}

document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById('searchForm');
    const resultsTableBody = document.getElementById('resultsTableBody');
    const owlAnimation = document.getElementById('owl-animation');
    const exportButton = document.getElementById('exportButton');

    searchForm.addEventListener('submit', function (event) {
        // Очищаем результаты
        resultsTableBody.innerHTML = '';

        // Показываем индикатор загрузки
        showLoadingIndicator();
    });

    exportButton.addEventListener('click', function (event) {
        // Предотвращаем действие по умолчанию (отправку GET-запроса)
        event.preventDefault();
        
        // Вызывайте функцию для экспорта результатов
        exportResultsToTxt();
    });
    
    function showLoadingIndicator() {
        // Показываем индикатор загрузки
        owlAnimation.style.display = 'flex';
        owlAnimation.style.justifyContent = 'center';
        owlAnimation.style.alignItems = 'center';
    }

    function tableToText(table) {
        // Преобразуйте таблицу в текстовое содержимое (например, CSV)
        // В этом примере, мы будем использовать запятые для разделения значений
        let textContent = Array.from(table.rows)
            .map(row => Array.from(row.cells).map(cell => cell.textContent).join(','))
            .join('\n');
        return textContent;
    }
    
    function exportResultsToTxt() {
        const resultsTable = document.getElementById('results-table');
        
        // Получите текстовое содержимое из столбца "Сообщение"
        const textContent = columnToText(resultsTable, 1); // 1 - индекс столбца "Сообщение"
    
        // Создайте Blob из текста
        const blob = createTxtBlob(textContent);
    
        // Создайте Blob URL
        const blobUrl = URL.createObjectURL(blob);
    
        // Создайте элемент <a> для скачивания файла
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = 'results.txt';
    
        // Добавьте элемент на страницу, эмулируйте клик для скачивания и удалите элемент
        document.body.appendChild(link);
        link.click();
    
        // Очистите Blob URL после использования
        URL.revokeObjectURL(blobUrl);
    
        document.body.removeChild(link);
    }
    
    function columnToText(table, columnIndex) {
        // Получите все ячейки в указанном столбце
        const cells = Array.from(table.querySelectorAll(`tr td:nth-child(${columnIndex + 1})`));
    
        // Извлеките текст из каждой ячейки и объедините их через перенос строки
        return cells.map(cell => cell.textContent.trim()).join('\n');
    }
    
    function createTxtBlob(text) {
        try {
            // Создайте Blob из текста
            return new Blob([text], { type: 'text/plain' });
        } catch (error) {
            console.error('Error creating Blob:', error);
            return null;
        }
    }
});