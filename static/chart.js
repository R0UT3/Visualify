document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('radarChart');
    if (!canvas) {
        console.error('Canvas not found');
        return;
    }

    const averageFeatures = JSON.parse(canvas.dataset.features);
    console.log('Average Features:', averageFeatures);
    
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
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: '#ffffff' },
                    grid: { color: '#888' },
                    pointLabels: { 
                        color: '#ffffff',
                        font: {
                            size: 14 // Increase font size of the labels
                        }
                    },
                    ticks: {
                        display: false
                    },
                    suggestedMin: 0,
                    suggestedMax: 1
                }
            }
        }
    };

    new Chart(canvas.getContext('2d'), config);
});