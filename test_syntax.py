#!/usr/bin/env python3
"""Test Python syntax without importing dependencies"""

import py_compile
import sys
from pathlib import Path

def check_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    # List of Python files to check
    python_files = [
        'main.py',
        'src/__init__.py',
        'src/document_processor.py',
        'src/parsers/__init__.py',
        'src/parsers/base_parser.py',
        'src/parsers/pdf_parser.py',
        'src/parsers/docx_parser.py',
        'src/parsers/xlsx_parser.py',
        'src/parsers/pptx_parser.py',
    ]

    all_valid = True
    for file_path in python_files:
        if Path(file_path).exists():
            valid, error = check_syntax(file_path)
            if valid:
                print(f"✓ {file_path}")
            else:
                print(f"✗ {file_path}: {error}")
                all_valid = False
        else:
            print(f"⚠ {file_path}: File not found")

    if all_valid:
        print("\n✓ All Python files have valid syntax!")
        return 0
    else:
        print("\n✗ Some files have syntax errors")
        return 1

if __name__ == '__main__':
    sys.exit(main())
