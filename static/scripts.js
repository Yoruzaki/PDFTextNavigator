const { useState } = React;

function App() {
    const [uploading, setUploading] = useState(false);
    const [searchResults, setSearchResults] = useState([]);
    const [error, setError] = useState(null);

    const handleFileUpload = async (event) => {
        event.preventDefault();
        setUploading(true);
        setError(null);

        let formData = new FormData();
        let fileInput = document.getElementById('file');
        formData.append('file', fileInput.files[0]);

        try {
            let response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                let blob = await response.blob();
                let link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = 'extracted_text.txt';
                link.click();
            } else {
                throw new Error('Failed to upload file');
            }
        } catch (error) {
            setError(`Error: ${error.message}`);
        } finally {
            setUploading(false);
        }
    };

    const handleSearch = async (event) => {
        event.preventDefault();
        setError(null);
        const searchTerm = document.getElementById('search-term').value;

        try {
            let response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ searchTerm })
            });
            let data = await response.json();
            if (data.results) {
                setSearchResults(data.results);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            setError(`Error: ${error.message}`);
        }
    };

    return (
        <div className="container">
            <h1 className="text-3xl font-bold mb-4">Upload PDF to Extract Text</h1>
            <form onSubmit={handleFileUpload} className="mb-8">
                <input type="file" id="file" name="file" accept=".pdf" required className="input mb-4" />
                <button type="submit" className="button" disabled={uploading}>
                    {uploading ? 'Uploading...' : 'Upload and Extract'}
                </button>
            </form>
            <div id="result" className="result">
                {error && <p className="text-red-500">{error}</p>}
            </div>

            <h2 className="text-2xl font-semibold mb-4">Search Text in All Extracted Files</h2>
            <form onSubmit={handleSearch}>
                <input type="text" id="search-term" name="search-term" placeholder="Enter search term" required className="input mb-4" />
                <button type="submit" className="button">Search</button>
            </form>
            <div id="search-result" className="result">
                {searchResults.map((result, index) => (
                    <div key={index}>
                        <strong>{result.filename} (Line {result.line}):</strong> {result.content}
                    </div>
                ))}
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('app'));
