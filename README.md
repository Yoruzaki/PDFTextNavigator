# PDF Text Extractor

**PDF Text Extractor** is a web application that allows users to upload PDF files, extract text from them, and search for specific terms within the extracted text. Built with Flask, PyMuPDF, and Tailwind CSS.
- **Upload PDF Files**: Easily upload PDF files to extract their text.
- **Text Extraction**: Converts the content of PDF files into text files.
- **Search Functionality**: Search for specific terms across all extracted text files.
- **User-Friendly Interface**: Modern and responsive design using Tailwind CSS.

## Technologies Used

- **Flask**: Web framework for building the web application.
- **PyMuPDF**: Library for extracting text from PDF files.
- **Tailwind CSS**: Utility-first CSS framework for styling.
- **JavaScript**: For handling client-side interactions and asynchronous operations.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- pip (Python package installer)

### Installation


1. **Install Dependencies:**

    Create a virtual environment and install the required Python packages.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

    The `requirements.txt` file should include:

    ```
    Flask
    PyMuPDF
    ```

2. **Run the Application:**

    Start the Flask development server.

    ```bash
    python app.py
    ```

    By default, the application will be accessible at `http://127.0.0.1:5000`.

## Usage

1. **Upload a PDF:**

    - Go to the home page.
    - Use the upload form to select and upload a PDF file.
    - The extracted text will be available for download.

2. **Search Extracted Text:**

    - After uploading PDFs, use the search form to find specific terms in all extracted text files.
    - Results will be displayed with filenames and line numbers.
