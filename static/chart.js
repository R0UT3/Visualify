const averageFeatures = JSON.parse('{{ average_features | safe }}');

document.addEventListener('DOMContentLoaded', () => {
    console.log('Parsed Average Features:', averageFeatures);
    
    const ctx = document.getElementById('radarChart');
    if (!ctx) {
        console.error('Canvas not found');
        return;
    }
    
    const data = {
        labels: Object.keys(averageFeatures),
        datasets: [{
            label: 'Your Favorite Characteristics',
            data: Object.values(averageFeatures),
            backgroundColor: 'rgba(29, 185, 84, 0.2)',
            borderColor: 'rgba(29, 185, 84, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(29, 185, 84, 1)'
        }]
    };

    const config = {
        type: 'radar',
        data: data,
        options: {
            responsive: true,
            scales: {
                r: {
                    angleLines: { color: '#ffffff' },
                    grid: { color: '#888' },
                    pointLabels: { color: '#ffffff' }
                }
            }
        }
    };

    new Chart(ctx.getContext('2d'), config);
});