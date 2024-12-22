function ingestData() {
    const urls = document.getElementById('urls').value.split('\n').map(url => url.trim()).filter(url => url);
    fetch('/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: urls })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => alert('Error: ' + error.message));
}

function searchQuery() {
    const query = document.getElementById('query').value;
    fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').textContent = data.response || 'No relevant information found.';
    })
    .catch(error => alert('Error: ' + error.message));
}