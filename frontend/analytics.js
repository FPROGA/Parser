document.addEventListener('DOMContentLoaded', async () => {
    try {
        const resumeResponse = await fetch('http://localhost:8000/get-analytics/');
        const resumeData = await resumeResponse.json();
        
        updateResumeAnalytics(resumeData);
        
    } catch (error) {
        console.error('Ошибка загрузки аналитики:', error);
        alert('Не удалось загрузить данные аналитики');
    }
});
document.addEventListener('DOMContentLoaded', function() {
    loadTopCandidates();
});

async function loadTopCandidates() {
    try {
        const response = await fetch('http://localhost:8000/get-top-candidates/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Received data:", data);
        const container = document.getElementById('top-candidates-list');
        container.innerHTML = '';
        
        for (const [profession, candidate] of Object.entries(data)) {
            const candidateElement = document.createElement('div');
            candidateElement.className = 'candidate-item';
            candidateElement.innerHTML = `
                <h3>${profession}</h3>
                <p>Лучший кандидат: <strong>${candidate.full_name}</strong></p>
                <p>Совпадение: <strong>${candidate.percent}%</strong></p>
            `;
            container.appendChild(candidateElement);
        }
    } catch (error) {
        console.error('Ошибка загрузки топ кандидатов:', error);
        document.getElementById('top-candidates-list').innerHTML = 
            '<p>Не удалось загрузить данные о топ кандидатах</p>';
    }
}
function updateResumeAnalytics(data) {
    document.getElementById('total-resumes').textContent = data.total_resumes;
    
    const topSkillsList = document.getElementById('top-skills-list');
    topSkillsList.innerHTML = ''; 
    const topSkills = data.top_hard_skills.slice(0, 5);
    
    topSkills.forEach(skill => {
        const skillItem = document.createElement('div');
        skillItem.className = 'skill-item';
        skillItem.innerHTML = `
            <span class="skill-name">${skill.skill}</span>
            <span class="skill-count">${skill.count}</span>
        `;
        topSkillsList.appendChild(skillItem);
    });

    const ctx = document.getElementById('skillsChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topSkills.map(skill => skill.skill),
            datasets: [{
                label: 'Количество упоминаний',
                data: topSkills.map(skill => skill.count),
                backgroundColor: [
                    'rgba(33, 150, 243, 0.7)',
                    'rgba(76, 175, 80, 0.7)',
                    'rgba(255, 152, 0, 0.7)',
                    'rgba(156, 39, 176, 0.7)',
                    'rgba(244, 67, 54, 0.7)'
                ],
                borderColor: [
                    'rgba(33, 150, 243, 1)',
                    'rgba(76, 175, 80, 1)',
                    'rgba(255, 152, 0, 1)',
                    'rgba(156, 39, 176, 1)',
                    'rgba(244, 67, 54, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}