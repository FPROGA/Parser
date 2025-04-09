document.getElementById('file1').addEventListener('change', (e) => {
  const fileName = e.target.files[0] ? e.target.files[0].name : 'Файл не выбран';
  document.getElementById('file1-name').textContent = fileName;
});

document.querySelector('.analyze-btn').addEventListener('click', async function() {
    const fileInput = document.getElementById('file1');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Пожалуйста, выберите файл!');
        return;
    }
  
    try {
        const response = await fetch('http://localhost:8000/upload-resume/', {
            method: 'POST',
            body: (() => {
                const formData = new FormData();
                formData.append('file', file);
                return formData;
            })()
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сервера');
        }
        
        const result = await response.json();
        console.log("Результат:", result);
        
        alert(`Анализ завершен! Проверьте консоль для подробностей`);
        
    } catch (error) {
        console.error('Полная ошибка:', error);
        alert(`Ошибка: ${error.message}`);
    }
  });