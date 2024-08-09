document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();

    let formData = new FormData();
    let fileInput = document.getElementById('file');
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Failed to upload file');
        }
    })
    .then(blob => {
        let link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'extracted_text.txt';
        link.click();
    })
    .catch(error => {
        document.getElementById('result').innerText = `Error: ${error.message}`;
    });
});

document.getElementById('search-form').addEventListener('submit', function(e) {
    e.preventDefault();

    let searchTerm = document.getElementById('search-term').value;

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ searchTerm })
    })
    .then(response => response.json())
    .then(data => {
        if (data.results) {
            let resultsHtml = data.results.map(result => 
                `<div><strong>${result.filename} (Line ${result.line}):</strong> ${result.content}</div>`
            ).join('');
            document.getElementById('search-result').innerHTML = resultsHtml;
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        document.getElementById('search-result').innerText = `Error: ${error.message}`;
    });
});
