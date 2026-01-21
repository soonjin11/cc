# Document Processing to Markdown Converter

A Python-based document processor that converts various document formats (PDF, DOCX, XLSX, PPTX) into well-formatted Markdown files.

## Features

- **Multi-format Support**: Process PDF, DOCX, XLSX, and PPTX files
- **Intelligent Parsing**:
  - Extracts text, tables, and structure from documents
  - Preserves formatting like headings, bold text
  - Handles multi-page documents
  - Extracts tables and converts them to Markdown format
- **Easy to Use**: Simple command-line interface
- **Clean Output**: Generates readable Markdown files

## Supported Formats

| Format | Extension | Features |
|--------|-----------|----------|
| PDF | `.pdf` | Text extraction, tables, page-by-page processing |
| Word | `.docx` | Headings, paragraphs, tables, formatting |
| Excel | `.xlsx` | Multiple sheets, all data as tables |
| PowerPoint | `.pptx` | Slides, titles, content, notes, tables |

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cc
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Convert a document to Markdown:
```bash
python main.py path/to/document.pdf
```

The output will be saved to `./output/document.md`

### Advanced Usage

Specify a custom output name:
```bash
python main.py document.docx -o my_custom_name
```

Specify a custom output directory:
```bash
python main.py document.xlsx --output-dir ./my_output
```

### Command-line Options

```
usage: main.py [-h] [-o OUTPUT_NAME] [--output-dir OUTPUT_DIR] file

positional arguments:
  file                  Path to the document file to convert

optional arguments:
  -h, --help            Show this help message and exit
  -o, --output-name     Custom name for the output markdown file
  --output-dir          Directory for output files (default: ./output)
```

## Examples

### Processing a PDF
```bash
python main.py uploads/report.pdf
# Output: output/report.md
```

### Processing a Word Document
```bash
python main.py uploads/proposal.docx -o project_proposal
# Output: output/project_proposal.md
```

### Processing an Excel Spreadsheet
```bash
python main.py uploads/data.xlsx
# Output: output/data.md (with all sheets as tables)
```

### Processing a PowerPoint Presentation
```bash
python main.py uploads/presentation.pptx
# Output: output/presentation.md (with all slides)
```

## Project Structure

```
.
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── __init__.py
│   ├── document_processor.py  # Main processor class
│   └── parsers/
│       ├── __init__.py
│       ├── base_parser.py     # Base parser class
│       ├── pdf_parser.py      # PDF parser
│       ├── docx_parser.py     # DOCX parser
│       ├── xlsx_parser.py     # XLSX parser
│       └── pptx_parser.py     # PPTX parser
├── uploads/               # Place your documents here (optional)
└── output/                # Generated markdown files
```

## How It Works

1. **File Detection**: The processor automatically detects the file type based on extension
2. **Parser Selection**: Selects the appropriate parser for the document type
3. **Content Extraction**: Extracts text, tables, formatting, and structure
4. **Markdown Conversion**: Converts extracted content to clean Markdown format
5. **File Generation**: Saves the result as a `.md` file

## Dependencies

- `pdfplumber` - PDF text and table extraction
- `python-docx` - Word document processing
- `openpyxl` - Excel spreadsheet processing
- `python-pptx` - PowerPoint presentation processing
- `Pillow` - Image processing support

## Output Format

The generated Markdown files include:

- **Document title** (from filename)
- **Source reference**
- **Structured content**:
  - Headings (for DOCX, PPTX)
  - Paragraphs
  - Tables in Markdown format
  - Page/sheet/slide numbers
  - Notes (for PPTX)

## Error Handling

The tool includes error handling for:
- File not found
- Unsupported file formats
- Corrupted documents
- Parsing errors

Errors are clearly reported with helpful messages.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is open-source and available for use.

## Tips

1. **For best results with PDFs**: Ensure the PDF contains selectable text (not scanned images)
2. **For Excel files**: All sheets are processed and included in the output
3. **For PowerPoint**: Both slide content and notes are extracted
4. **For Word documents**: Heading styles are preserved as Markdown headings

## Troubleshooting

**Q: PDF extraction is empty**
A: The PDF might be image-based. Consider using OCR preprocessing.

**Q: Tables look incorrect**
A: Complex table structures might not convert perfectly. Check the source document.

**Q: Missing dependencies**
A: Run `pip install -r requirements.txt` to install all required packages.

## Future Enhancements

Possible future features:
- Image extraction and embedding
- OCR support for scanned PDFs
- HTML output format
- Batch processing
- Web interface
- More format support (ODT, RTF, etc.)
