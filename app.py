from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF
import os

app = Flask(__name__)

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
        pdf_path = os.path.join('uploads', filename)
        txt_path = os.path.join('uploads', filename.rsplit('.', 1)[0] + '.txt')
        
        file.save(pdf_path)
        
        success = extract_text(pdf_path, txt_path)
        if success:
            return send_file(txt_path, as_attachment=True)
        else:
            return jsonify({"error": "Failed to extract text"}), 500
    
    return jsonify({"error": "Invalid file format"}), 400

@app.route('/search', methods=['POST'])
def search_text():
    data = request.json
    search_term = data.get('searchTerm')
    
    if not search_term:
        return jsonify({"error": "Search term is required"}), 400
    
    folder_path = 'uploads'
    
    if not os.path.exists(folder_path):
        return jsonify({"error": "Uploads folder does not exist"}), 404
    
    results = []
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, start=1):
                        if search_term.lower() in line.lower():
                            results.append({
                                'filename': filename,
                                'line': line_num,
                                'content': line.strip()
                            })
        
        return jsonify({"results": results})
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "Failed to search text"}), 500

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
