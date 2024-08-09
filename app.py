from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from config import CLOUD_FLARE_R2_ACCESS_KEY_ID, CLOUD_FLARE_R2_SECRET_ACCESS_KEY, CLOUD_FLARE_R2_BUCKET, CLOUD_FLARE_R2_ENDPOINT
import tempfile
import os

app = Flask(__name__)

# Initialize boto3 client for Cloudflare R2
s3_client = boto3.client(
    's3',
    endpoint_url=CLOUD_FLARE_R2_ENDPOINT,
    aws_access_key_id=CLOUD_FLARE_R2_ACCESS_KEY_ID,
    aws_secret_access_key=CLOUD_FLARE_R2_SECRET_ACCESS_KEY
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
        print(f"An unexpected error occurred during text extraction: {e}")
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
        with tempfile.TemporaryDirectory() as tmpdirname:
            pdf_path = os.path.join(tmpdirname, file.filename)
            txt_path = os.path.join(tmpdirname, file.filename.rsplit('.', 1)[0] + '.txt')

            file.save(pdf_path)
            print(f"PDF saved to {pdf_path}")

            success = extract_text(pdf_path, txt_path)
            if success:
                try:
                    s3_client.upload_file(txt_path, CLOUD_FLARE_R2_BUCKET, file.filename.rsplit('.', 1)[0] + '.txt')
                    print(f"Uploaded text file to bucket '{CLOUD_FLARE_R2_BUCKET}' with key '{file.filename.rsplit('.', 1)[0] + '.txt'}'")
                    return jsonify({"message": "File uploaded successfully"}), 200
                except NoCredentialsError:
                    print("Credentials not available.")
                    return jsonify({"error": "Credentials not available"}), 500
                except ClientError as e:
                    print(f"Client error occurred: {e}")
                    return jsonify({"error": f"Client error occurred: {e}"}), 500
                except Exception as e:
                    print(f"Failed to upload file: {e}")
                    return jsonify({"error": f"Failed to upload file: {e}"}), 500
            else:
                print("Failed to extract text.")
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
        for obj in s3_client.list_objects_v2(Bucket=CLOUD_FLARE_R2_BUCKET).get('Contents', []):
            if obj['Key'].endswith('.txt'):
                txt_file = s3_client.get_object(Bucket=CLOUD_FLARE_R2_BUCKET, Key=obj['Key'])
                content = txt_file['Body'].read().decode('utf-8')

                for line_num, line in enumerate(content.split('\n'), start=1):
                    if search_term.lower() in line.lower():
                        results.append({
                            'filename': obj['Key'],
                            'line': line_num,
                            'content': line.strip()
                        })

        return jsonify({"results": results})

    except Exception as e:
        print(f"An unexpected error occurred during search: {e}")
        return jsonify({"error": "Failed to search text"}), 500

if __name__ == '__main__':
    app.run(debug=True)
