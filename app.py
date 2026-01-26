import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path
from src.document_processor import DocumentProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure folders exist
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(parents=True, exist_ok=True)

# Initialize document processor
processor = DocumentProcessor(output_dir=app.config['OUTPUT_FOLDER'])

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.pptx'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html',
                         supported_formats=', '.join(ALLOWED_EXTENSIONS))


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash(f'Unsupported file format. Please upload: {", ".join(ALLOWED_EXTENSIONS)}', 'error')
        return redirect(url_for('index'))

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_path = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(upload_path))

        # Process document
        output_file = processor.process_document(str(upload_path))

        # Send the markdown file to user
        return send_file(
            output_file,
            as_attachment=True,
            download_name=f"{Path(filename).stem}.md",
            mimetype='text/markdown'
        )

    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('index'))

    finally:
        # Clean up uploaded file
        if upload_path.exists():
            upload_path.unlink()


@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'supported_formats': list(ALLOWED_EXTENSIONS)}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
