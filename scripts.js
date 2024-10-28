document.getElementById('spotify-form').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent the default form submission
    const username = document.getElementById('username').value;

    try {
        // Send the Spotify username to the backend
        const response = await fetch('http://127.0.0.1:5000/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });

        if (response.ok) {
            const data = await response.json();
            // Display the data or redirect to another page with results
            document.getElementById('result').innerHTML = `
                <h3>Analysis complete! See your results:</h3>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;
        } else {
            document.getElementById('result').textContent = 'Error analyzing Spotify data!';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').textContent = 'An error occurred while fetching the data.';
    }
});
