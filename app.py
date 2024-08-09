from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF
import os
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# Cloudflare R2 credentials
r2_access_key = 'M1862jBiU1Fpis-WqLlE1cvwy_4vnYYiGjygDP11'  
r2_secret_key = ''  
r2_endpoint_url = 'https://your-account-id.r2.cloudflarestorage.com'
r2_bucket_name = 'pdftext'

# Initialize R2 client
s3_client = boto3.client('s3',
    endpoint_url=r2_endpoint_url,
    aws_access_key_id=r2_access_key,
    aws_secret_access_key=r2_secret_key
)

def extract_text(pdf_path, output_txt_path):
    try:
        doc = fitz.open(pdf_path)
        full_text = ''
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            full_text += (page.get_text() or '') + '\n'
        
        # Write the extracted text to a file
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        return True
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = file.filename
        pdf_path = os.path.join('/tmp', filename)  # Temporary path for processing
        txt_path = os.path.join('/tmp', filename.rsplit('.', 1)[0] + '.txt')
        
        file.save(pdf_path)
        
        success = extract_text(pdf_path, txt_path)
        if success:
            # Upload the text file to R2
            try:
                s3_client.upload_file(txt_path, r2_bucket_name, filename.rsplit('.', 1)[0] + '.txt')
                # Return the file URL from R2
                file_url = f"{r2_endpoint_url}/{r2_bucket_name}/{filename.rsplit('.', 1)[0] + '.txt'}"
                return jsonify({"file_url": file_url})
            except NoCredentialsError:
                return jsonify({"error": "Credentials not available"}), 500
        else:
            return jsonify({"error": "Failed to extract text"}), 500
    
    return jsonify({"error": "Invalid file format"}), 400

@app.route('/search', methods=['POST'])
def search_text():
    data = request.json
    search_term = data.get('searchTerm')
    
    if not search_term:
        return jsonify({"error": "Search term is required"}), 400
    
    results = []
    try:
        # List all files in the R2 bucket
        response = s3_client.list_objects_v2(Bucket=r2_bucket_name)
        
        for obj in response.get('Contents', []):
            filename = obj['Key']
            if filename.endswith('.txt'):
                # Download the file from R2
                s3_client.download_file(r2_bucket_name, filename, filename)
                
                with open(filename, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, start=1):
                        if search_term.lower() in line.lower():
                            results.append({
                                'filename': filename,
                                'line': line_num,
                                'content': line.strip()
                            })
                
                os.remove(filename)  # Remove the file after processing
        
        return jsonify({"results": results})
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "Failed to search text"}), 500

if __name__ == '__main__':
    app.run(debug=True)
