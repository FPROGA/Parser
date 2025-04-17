document.addEventListener('DOMContentLoaded', async () => {
    const loader = document.getElementById('loader');
    const loadingText = document.getElementById('loading-text'); 
    
    try {
        loader.style.display = 'block';
        loadingText.style.display = 'block'; 
        
        const vacanciesResponse = await fetch('http://localhost:8000/get-vacancies-analytics/');
        const vacanciesData = await vacanciesResponse.json();

        updateVacanciesAnalytics(vacanciesData);
        
    } catch (error) {
        console.error('Ошибка загрузки аналитики вакансий:', error);
        alert('Не удалось загрузить данные о вакансиях');
    } finally {
        loader.style.display = 'none';
        loadingText.style.display = 'none'; 
    }
});

function updateVacanciesAnalytics(data) {
    const tabsContainer = document.getElementById('profession-tabs');
    const statsContainer = document.getElementById('vacancy-stats');
    
    tabsContainer.innerHTML = '';
    statsContainer.innerHTML = '';
    
    data.forEach((profession, index) => {
        const tab = document.createElement('div');
        tab.className = `profession-tab ${index === 0 ? 'active' : ''}`;
        tab.textContent = profession.profession;
        tab.dataset.index = index;
        tab.addEventListener('click', () => switchProfessionTab(index, data));
        tabsContainer.appendChild(tab);
        
        const statCard = document.createElement('div');
        statCard.className = 'vacancy-stat-card';
        statCard.innerHTML = `
            <h3>${profession.profession}</h3>
            <p>Вакансий: <strong>${profession.vacancies_count}</strong></p>
            <p>Навыков: <strong>${profession.total_skills}</strong></p>
            <p>Уникальных: <strong>${profession.unique_skills}</strong></p>
        `;
        statsContainer.appendChild(statCard);
    });
    
    if (data.length > 0) {
        updateVacancyChart(data[0]);
    }
}

function switchProfessionTab(index, data) {
    document.querySelectorAll('.profession-tab').forEach((tab, i) => {
        tab.classList.toggle('active', i === index);
    });

    updateVacancyChart(data[index]);
}

function updateVacancyChart(professionData) {
    const ctx = document.getElementById('vacancySkillsChart').getContext('2d');
    
    if (window.vacancyChart) {
        window.vacancyChart.destroy();
    }
    
    const sortedSkills = [...professionData.top_skills].sort((a, b) => b.count - a.count);
    
    window.vacancyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedSkills.map(item => item.skill),
            datasets: [{
                label: 'Количество упоминаний в вакансиях',
                data: sortedSkills.map(item => item.count),
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
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
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}
