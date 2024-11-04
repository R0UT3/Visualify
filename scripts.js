document.getElementById('spotify-form').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent the default form submission
    const username = document.getElementById('username').value;
    console.log('Username:', username); // Make sure this logs the expected value

    try {
        // Send the Spotify username to the backend
        const response = await fetch(`https://visualifybackend.onrender.com/analyze?username=${encodeURIComponent(username)}`, {
            method: 'GET'
        });
        console.log("hasta aqui")
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
