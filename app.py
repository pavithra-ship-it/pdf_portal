from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from werkzeug.utils import secure_filename
from fpdf import FPDF
from PyPDF2 import PdfMerger


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

# 1. Merge PDFs

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('pdf_files')
    merger = PdfMerger()

    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        try:
            merger.append(filepath)
        except Exception as e:
            return f"Error appending {filename}: {e}"

    output_path = os.path.join(PROCESSED_FOLDER, 'merged.pdf')
    try:
        merger.write(output_path)
        merger.close()
        print("PDF merged successfully")
    except Exception as e:
        return f"Write failed: {e}"

    return send_file(output_path, as_attachment=True)

# 2. Edit (example: remove first page)
@app.route('/edit', methods=['POST'])
def edit_pdf():
    file = request.files['pdf_file']
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(filepath)

    reader = PdfReader(filepath)
    writer = PdfWriter()
    for page_num in range(1, len(reader.pages)):  # Skips the first page
        writer.add_page(reader.pages[page_num])
    
    output_path = os.path.join(PROCESSED_FOLDER, 'edited.pdf')
    with open(output_path, 'wb') as f:
        writer.write(f)
    
    return send_file(output_path, as_attachment=True)

# 3. Organize (example: reverse page order)
@app.route('/organize', methods=['POST'])
def organize_pdf():
    file = request.files['pdf_file']
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(filepath)

    reader = PdfReader(filepath)
    writer = PdfWriter()

    for page in reversed(reader.pages):
        writer.add_page(page)

    output_path = os.path.join(PROCESSED_FOLDER, 'organized.pdf')
    with open(output_path, 'wb') as f:
        writer.write(f)

    return send_file(output_path, as_attachment=True)

# 4. Convert to PDF (from text)
@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    text = request.form['text_content']
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)
    
    output_path = os.path.join(PROCESSED_FOLDER, 'converted.pdf')
    pdf.output(output_path)
    
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
