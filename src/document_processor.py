from pathlib import Path
from typing import Optional
from .parsers import PDFParser, DOCXParser, XLSXParser, PPTXParser


class DocumentProcessor:
    """Main document processor that handles various document formats"""

    SUPPORTED_FORMATS = {
        '.pdf': PDFParser,
        '.docx': DOCXParser,
        '.xlsx': XLSXParser,
        '.pptx': PPTXParser,
    }

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_document(self, file_path: str, output_name: Optional[str] = None) -> str:
        """
        Process a document and convert it to markdown

        Args:
            file_path: Path to the document file
            output_name: Optional custom name for output file (without extension)

        Returns:
            Path to the generated markdown file
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file extension
        extension = file_path.suffix.lower()

        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS.keys())}"
            )

        # Get appropriate parser
        parser_class = self.SUPPORTED_FORMATS[extension]
        parser = parser_class(str(file_path))

        # Generate output filename
        if output_name:
            output_file = self.output_dir / f"{output_name}.md"
        else:
            output_file = self.output_dir / f"{file_path.stem}.md"

        # Parse and save
        parser.save_markdown(str(output_file))

        return str(output_file)

    @staticmethod
    def get_supported_formats() -> list:
        """Return list of supported file formats"""
        return list(DocumentProcessor.SUPPORTED_FORMATS.keys())
