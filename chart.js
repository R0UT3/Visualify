// Data passed from Flask backend
const averageFeatures = JSON.parse('{{ average_features | tojson | safe }}');
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('Average Features:', averageFeatures);
        const ctx = document.getElementById('radarChart');
        if (!ctx) {
            console.error('Canvas not found');
            return;
        }
        new Chart(ctx.getContext('2d'), config);
    } catch (error) {
        console.error('Chart rendering error:', error);
    }
});
// Prepare data for the radar chart
const data = {
    labels: Object.keys(averageFeatures),
    datasets: [{
        label: 'Your Favorite Characteristics',
        data: Object.values(averageFeatures),
        backgroundColor: 'rgba(29, 185, 84, 0.2)', // Spotify green with transparency
        borderColor: 'rgba(29, 185, 84, 1)',       // Spotify green
        borderWidth: 2,
        pointBackgroundColor: 'rgba(29, 185, 84, 1)'
    }]
};

// Radar chart configuration
const config = {
    type: 'radar',
    data: data,
    options: {
        responsive: true,
        scales: {
            r: {
                angleLines: { color: '#ffffff' },  // White grid lines
                grid: { color: '#888' },          // Grey grid lines
                pointLabels: { color: '#ffffff' } // White labels
            }
        }
    }
};

// Render the radar chart
const ctx = document.getElementById('radarChart').getContext('2d');
new Chart(ctx, config);