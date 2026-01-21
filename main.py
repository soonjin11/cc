#!/usr/bin/env python3
"""
Document Processing to Markdown Converter
Supports: PDF, DOCX, XLSX, PPTX
"""

import sys
import argparse
from pathlib import Path
from src.document_processor import DocumentProcessor


def main():
    parser = argparse.ArgumentParser(
        description='Convert documents (PDF, DOCX, XLSX, PPTX) to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py document.pdf
  python main.py document.docx -o custom_name
  python main.py document.xlsx --output-dir ./my_output
        """
    )

    parser.add_argument(
        'file',
        help='Path to the document file to convert'
    )

    parser.add_argument(
        '-o', '--output-name',
        help='Custom name for the output markdown file (without .md extension)',
        default=None
    )

    parser.add_argument(
        '--output-dir',
        help='Directory for output files (default: ./output)',
        default='output'
    )

    args = parser.parse_args()

    # Check if file exists
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Create processor
    processor = DocumentProcessor(output_dir=args.output_dir)

    # Process document
    try:
        print(f"Processing: {args.file}")
        output_file = processor.process_document(args.file, args.output_name)
        print(f"✓ Successfully converted to: {output_file}")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
