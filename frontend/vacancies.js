document.addEventListener('DOMContentLoaded', async () => {
    const loader = document.getElementById('loader');
    const loadingText = document.getElementById('loading-text');
    
    try {
        // Показываем лоадер и текст
        loader.style.display = 'block';
        loadingText.style.display = 'block';
        
        // Загружаем данные о вакансиях с HeadHunter
        const hhResponse = await fetch('http://localhost:8000/get-vacancies-analytics/');
        const hhData = await hhResponse.json();
        
        // Обновляем данные о вакансиях
        updateVacanciesAnalytics(hhData, 'hh');
        
        // Инициализируем график
        if (hhData.length > 0) {
            updateVacancyChart(hhData[0], 'vacancySkillsChart', 'HeadHunter');
        }
        
    } catch (error) {
        console.error('Ошибка загрузки аналитики вакансий:', error);
        alert('Не удалось загрузить данные о вакансиях');
    } finally {
        // Скрываем лоадер и текст в любом случае
        loader.style.display = 'none';
        loadingText.style.display = 'none';
    }
});

function updateVacanciesAnalytics(data, source) {
    const tabsContainer = document.getElementById(`${source}-profession-tabs`);
    const statsContainer = document.getElementById(`${source}-vacancy-stats`);
    
    // Очищаем контейнеры перед обновлением
    tabsContainer.innerHTML = '';
    statsContainer.innerHTML = '';
    
    // Проверяем, что данные существуют и являются массивом
    if (!Array.isArray(data) || data.length === 0) {
        statsContainer.innerHTML = '<p>Нет данных о вакансиях</p>';
        return;
    }
    
    // Создаем табы для профессий
    data.forEach((profession, index) => {
        // Проверяем, что объект профессии содержит необходимые поля
        if (!profession || !profession.profession) {
            console.error('Неверный формат данных профессии:', profession);
            return;
        }

        // Создаем таб
        const tab = document.createElement('div');
        tab.className = `profession-tab ${index === 0 ? 'active' : ''}`;
        tab.textContent = profession.profession;
        tab.dataset.index = index;
        tab.addEventListener('click', () => switchProfessionTab(index, data, source));
        tabsContainer.appendChild(tab);
    });
    
    // Создаем карточки статистики
    data.forEach(profession => {
        const statCard = document.createElement('div');
        statCard.className = 'vacancy-stat-card';
        statCard.innerHTML = `
            <h3>${profession.profession}</h3>
            <p>Вакансий: <strong>${profession.vacancies_count || 0}</strong></p>
            <p>Навыков: <strong>${profession.total_skills || 0}</strong></p>
            <p>Уникальных: <strong>${profession.unique_skills || 0}</strong></p>
        `;
        statsContainer.appendChild(statCard);
    });
}

function switchProfessionTab(index, data, source) {
    // Обновляем активный таб
    document.querySelectorAll(`#${source}-profession-tabs .profession-tab`).forEach((tab, i) => {
        tab.classList.toggle('active', i === index);
    });
    
    // Обновляем график
    updateVacancyChart(data[index], 'vacancySkillsChart', 'HeadHunter');
}

function updateVacancyChart(professionData, chartId, sourceName) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    // Удаляем предыдущий график, если он существует
    if (window[`${chartId}Chart`]) {
        window[`${chartId}Chart`].destroy();
    }
    
    // Проверяем, есть ли данные для графика
    if (!professionData || !Array.isArray(professionData.top_skills) || professionData.top_skills.length === 0) {
        ctx.font = '16px Arial';
        ctx.fillStyle = '#666';
        ctx.textAlign = 'center';
        ctx.fillText('Нет данных о навыках', ctx.canvas.width/2, ctx.canvas.height/2);
        return;
    }
    
    // Подготавливаем данные для графика
    const labels = professionData.top_skills.map(item => item.skill);
    const data = professionData.top_skills.map(item => item.count);
    const backgroundColors = [
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(199, 199, 199, 0.6)',
        'rgba(83, 102, 255, 0.6)',
        'rgba(255, 99, 71, 0.6)',
        'rgba(34, 139, 34, 0.6)'
    ];
    
    // Создаем новый график
    window[`${chartId}Chart`] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Топ навыков (${sourceName})`,
                data: data,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Топ навыков для ${professionData.profession}`,
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество упоминаний'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Навыки'
                    }
                }
            }
        }
    });
}